import api, {
  GetPotentialUsersApiResponse,
  useAppDispatch,
  useCreateUserMutation,
  useGetPotentialUsersQuery,
  UserCreateRead,
} from 'api'
import { showNotification } from 'comps/notification'
import { UsersInvite } from 'features/invite/schema'
import { getAPIErrorMessage } from 'utils'

type PotentialUser = GetPotentialUsersApiResponse[number]

export interface EmailProblem {
  reason: string
  emails: string[]
}

interface UseInviteUsersOptions {
  workspaceDomain: string
  accountsUrl: string
}

export const useInviteUsers = ({
  workspaceDomain,
  accountsUrl,
}: UseInviteUsersOptions) => {
  const directory = useGetPotentialUsersQuery()
  const [createUser] = useCreateUserMutation()
  const dispatch = useAppDispatch()

  const usersByEmail: Record<string, PotentialUser> = Object.fromEntries(
    directory.data?.map((user) => [user.email.toLowerCase(), user]) || []
  )

  const fullName = (email: string) => {
    const user = usersByEmail[email]
    return user ? `${user.first_name} ${user.last_name}` : ''
  }

  // Emails that can't be invited, grouped by reason. Empty groups are left out.
  const findProblems = (emails: string[]): EmailProblem[] => {
    const suffix = `@${workspaceDomain}`
    return [
      {
        reason: `Not an ${suffix} address`,
        emails: emails.filter((e) => !e.endsWith(suffix)),
      },
      {
        reason: 'Not in the Google directory or already has an account',
        emails: emails.filter((e) => e.endsWith(suffix) && !usersByEmail[e]),
      },
    ].filter((p) => p.emails.length > 0)
  }

  // Invite everyone in one batch and notify the results. Resolves to the
  // emails that failed, so the caller can keep them for a retry.
  const inviteUsers = async ({
    users,
    groups,
    is_intern,
  }: UsersInvite): Promise<string[]> => {
    const results = await Promise.allSettled(
      users.map((email) => {
        const { first_name, last_name } = usersByEmail[email]
        return createUser({
          userCreate: { email, first_name, last_name, groups, is_intern },
        }).unwrap()
      })
    )

    const created: UserCreateRead[] = []
    const failed: string[] = []
    results.forEach((result, index) => {
      if (result.status === 'fulfilled') {
        created.push(result.value)
        return
      }
      failed.push(users[index])
      showNotification({
        type: 'error',
        title: `Couldn't invite ${users[index]}`,
        message: getAPIErrorMessage(result.reason),
        autoClose: false,
      })
    })
    if (created.length > 0) {
      showInvitedNotification(created, accountsUrl)
      // The directory list is slow to fetch, so refresh it once per batch.
      dispatch(api.util.invalidateTags(['POTENTIAL_USER']))
    }
    return failed
  }

  return {
    directory,
    emails: Object.keys(usersByEmail),
    fullName,
    findProblems,
    inviteUsers,
  }
}

const showInvitedNotification = (
  created: UserCreateRead[],
  accountsUrl: string
) => {
  const [first] = created
  showNotification({
    type: 'success',
    title: `Invited ${pluralise(created.length, 'user')}`,
    message:
      created.length === 1
        ? `Invitation sent to ${first.email}.`
        : 'Invitations sent.',
    // One link per user doesn't fit in a toast, so larger batches link to the
    // accounts list.
    link:
      created.length === 1
        ? { text: 'View user', url: first.url }
        : { text: 'View accounts', url: accountsUrl },
    autoClose: 4000,
  })
}

const pluralise = (count: number, noun: string) =>
  `${count} ${noun}${count === 1 ? '' : 's'}`
