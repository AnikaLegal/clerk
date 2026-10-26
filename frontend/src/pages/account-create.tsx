import { Anchor, Button, Container, Group, Text, Title } from '@mantine/core'
import api, { useAppDispatch, useCreateUserMutation, UserCreateRead } from 'api'
import { showNotification } from 'comps/notification'
import {
  InviteForm,
  InviteFormControlProps,
  InviteFormType,
  UsersCreate,
} from 'features/invite'
import React from 'react'
import { getAPIErrorMessage, mount } from 'utils'

interface DjangoContext {
  accounts_url: string
  group_values: string[]
  workspace_domain: string
}
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const CONTEXT = (window as any).REACT_CONTEXT as DjangoContext

const App = () => {
  const [createUser] = useCreateUserMutation()
  const dispatch = useAppDispatch()

  const handleSubmit = (form: InviteFormType, values: UsersCreate) => {
    form.setSubmitting(true)

    const promises = values.users.map((user) =>
      createUser({
        userCreate: {
          email: user.email,
          first_name: user.first_name,
          last_name: user.last_name,
          groups: values.groups,
          is_intern: values.is_intern,
        },
      }).unwrap()
    )
    Promise.allSettled(promises)
      .then((results) => {
        const created: UserCreateRead[] = []
        const failed = new Set<string>()
        results.forEach((result, index) => {
          if (result.status === 'fulfilled') {
            created.push(result.value)
            return
          }
          const email = values.users[index].email
          failed.add(email.toLowerCase())
          showNotification({
            type: 'error',
            title: `Couldn't invite ${email}`,
            message: getAPIErrorMessage(result.reason),
            autoClose: false,
          })
        })
        if (created.length > 0) {
          showInvitedNotification(created)
          dispatch(api.util.invalidateTags(['POTENTIAL_USER']))
        }
        if (failed.size === 0) {
          form.reset()
          return
        }
        // Keep only the failed emails so a retry doesn't re-invite the rest.
        form.setFieldValue(
          'users',
          form.getValues().users.filter((email) => failed.has(email))
        )
      })
      .finally(() => {
        form.setSubmitting(false)
      })
  }

  return (
    <Container size="md">
      <Title order={1}>Invite users</Title>
      <Anchor href={CONTEXT.accounts_url} size="sm">
        Back to accounts
      </Anchor>
      <Text c="dimmed" mt="xs" mb="md">
        Creates a Clerk account and Microsoft 365 login, and emails the sign-in
        details. Microsoft access can take up to 15 minutes.
      </Text>
      <InviteForm
        groups={CONTEXT.group_values}
        workspaceDomain={CONTEXT.workspace_domain}
        onSubmit={handleSubmit}
        onCancel={() => {
          /* Do nothing */
        }}
        controls={InviteFormControls}
      />
    </Container>
  )
}

const showInvitedNotification = (created: UserCreateRead[]) => {
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
        : { text: 'View accounts', url: CONTEXT.accounts_url },
    autoClose: 4000,
  })
}

const pluralise = (count: number, noun: string) =>
  `${count} ${noun}${count === 1 ? '' : 's'}`

const InviteFormControls = ({ form }: InviteFormControlProps) => {
  return (
    <Group mt="lg">
      <Button
        type="submit"
        disabled={form.submitting}
        loading={form.submitting}
        size="md"
      >
        Invite users
      </Button>
    </Group>
  )
}

mount(App)
