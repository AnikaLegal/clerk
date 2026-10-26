import {
  Alert,
  Button,
  Checkbox,
  ComboboxItem,
  ComboboxLikeRenderOptionInput,
  ComboboxStringItem,
  Group,
  List,
  Loader,
  MultiSelect,
  OptionsFilter,
  TagsInput,
  Text,
} from '@mantine/core'
import { useForm } from '@mantine/form'
import {
  EmailProblem,
  useInviteUsers,
} from 'features/invite/hooks/use-invite-users'
import { UsersInvite, UsersInviteSchema } from 'features/invite/schema'
import { yupResolver } from 'mantine-form-yup-resolver'
import React, { useState } from 'react'

export interface InviteFormProps {
  groups: string[]
  workspaceDomain: string
  accountsUrl: string
}

export const InviteForm = ({
  groups,
  workspaceDomain,
  accountsUrl,
}: InviteFormProps) => {
  const { directory, emails, fullName, findProblems, inviteUsers } =
    useInviteUsers({ workspaceDomain, accountsUrl })
  const form = useForm<UsersInvite>({
    // Controlled, so the pills show the normalised (lowercased) emails.
    mode: 'controlled',
    initialValues: { users: [], groups: [], is_intern: true },
    validate: yupResolver(UsersInviteSchema),
  })
  const [problems, setProblems] = useState<EmailProblem[]>([])
  const [search, setSearch] = useState('')
  const problemCount = problems.reduce((n, p) => n + p.emails.length, 0)

  // Match on name as well as email, so people can be found by name.
  const filterByNameOrEmail: OptionsFilter = ({ options, search }) => {
    const query = search.trim().toLowerCase()
    return (options as ComboboxItem[]).filter((option) =>
      `${fullName(option.value)} ${option.value}`.toLowerCase().includes(query)
    )
  }

  const renderUserOption = ({
    option,
  }: ComboboxLikeRenderOptionInput<ComboboxStringItem>) => (
    <div>
      <Text size="md">{fullName(option.value) || option.value}</Text>
      <Text size="sm" opacity={0.5}>
        {option.value}
      </Text>
    </div>
  )

  const showProblems = (next: EmailProblem[]) => {
    const remaining = next.filter((p) => p.emails.length > 0)
    const count = remaining.reduce((n, p) => n + p.emails.length, 0)
    setProblems(remaining)
    if (count > 0) {
      form.setFieldError(
        'users',
        count === 1
          ? "1 address can't be invited"
          : `${count} addresses can't be invited`
      )
    } else {
      form.clearFieldError('users')
    }
  }

  const removeProblemEmails = () => {
    const bad = new Set(problems.flatMap((p) => p.emails))
    form.setFieldValue(
      'users',
      form.getValues().users.filter((e) => !bad.has(e))
    )
    showProblems([])
  }

  const handleSubmit = async (values: UsersInvite) => {
    if (directory.isLoading) {
      form.setFieldError(
        'users',
        'Still loading the Google directory, try again in a moment.'
      )
      return
    }
    if (directory.isError) {
      return
    }
    const found = findProblems(values.users)
    if (found.length > 0) {
      showProblems(found)
      return
    }

    form.setSubmitting(true)
    try {
      const failed = await inviteUsers(values)
      if (failed.length === 0) {
        form.reset()
      } else {
        // Keep only the failed emails so a retry doesn't re-invite the rest.
        form.setFieldValue('users', failed)
      }
    } finally {
      form.setSubmitting(false)
    }
  }

  const usersInputProps = form.getInputProps('users')

  return (
    <form autoComplete="off" onSubmit={form.onSubmit(handleSubmit)}>
      <TagsInput
        {...usersInputProps}
        onChange={(value) => {
          const users = [...new Set(value.map((e) => e.trim().toLowerCase()))]
          usersInputProps.onChange(users)
          if (problems.length > 0) {
            // Drop problems whose emails were removed by hand.
            showProblems(
              problems.map((p) => ({
                ...p,
                emails: p.emails.filter((e) => users.includes(e)),
              }))
            )
          }
        }}
        error={
          usersInputProps.error ||
          (directory.isError &&
            "Couldn't load the Google directory. Reload the page to try again.")
        }
        label="Users"
        placeholder="Enter, select or paste email addresses..."
        data={emails}
        filter={filterByNameOrEmail}
        renderOption={renderUserOption}
        searchValue={search}
        onSearchChange={setSearch}
        // Enter picks the highlighted person rather than adding a name as
        // typed. Only while searching, or picking scrolls the list to the top.
        selectFirstOptionOnChange={search !== ''}
        rightSection={directory.isLoading ? <Loader size="sm" /> : undefined}
        splitChars={[',', ' ', '|', ';', '\n']}
        clearable
        size="md"
      />
      {problemCount > 0 && (
        <Alert color="red" variant="light" mt="xs">
          {problems.map((p) => (
            <React.Fragment key={p.reason}>
              <Text size="sm" fw={500}>
                {p.reason}
              </Text>
              <List size="sm" mb="xs">
                {p.emails.map((e) => (
                  <List.Item key={e}>{e}</List.Item>
                ))}
              </List>
            </React.Fragment>
          ))}
          <Button
            size="xs"
            variant="light"
            color="red"
            onClick={removeProblemEmails}
          >
            {problemCount === 1
              ? 'Remove this address'
              : `Remove these ${problemCount} addresses`}
          </Button>
        </Alert>
      )}
      <MultiSelect
        {...form.getInputProps('groups')}
        label="Groups"
        data={groups}
        searchable
        clearable
        size="md"
        mt="md"
      />
      <Checkbox
        {...form.getInputProps('is_intern', { type: 'checkbox' })}
        label="Intern"
        size="md"
        mt="md"
      />
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
    </form>
  )
}
