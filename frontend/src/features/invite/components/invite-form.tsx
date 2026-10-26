import {
  Alert,
  Button,
  Checkbox,
  ComboboxItem,
  ComboboxLikeRenderOptionInput,
  ComboboxStringItem,
  List,
  Loader,
  MultiSelect,
  OptionsFilter,
  TagsInput,
  Text,
} from '@mantine/core'
import { useForm, UseFormInput } from '@mantine/form'
import { useGetPotentialUsersQuery } from 'api'
import { UsersCreate, UsersInvite, UsersInviteSchema } from 'features/invite'
import { yupResolver } from 'mantine-form-yup-resolver'
import React, { useState } from 'react'

export type InviteFormType = ReturnType<typeof useForm<UsersInvite>>

interface EmailProblem {
  reason: string
  emails: string[]
}

export interface InviteFormControlProps {
  form: InviteFormType
  onSubmit: (form: InviteFormType, values: UsersCreate) => void
  onCancel: () => void
}

export interface InviteFormProps {
  groups: string[]
  workspaceDomain: string
  onSubmit: (form: InviteFormType, values: UsersCreate) => void
  onCancel: () => void
  input?: UseFormInput<UsersInvite>
  controls?: React.ComponentType<InviteFormControlProps>
}

export const InviteForm = ({
  groups,
  workspaceDomain,
  onSubmit,
  onCancel,
  input,
  controls,
}: InviteFormProps) => {
  const potentialUserResult = useGetPotentialUsersQuery()
  const usersByEmail = Object.fromEntries(
    potentialUserResult.data?.map((user) => [user.email.toLowerCase(), user]) ||
      []
  )
  const fullName = (email: string) => {
    const user = usersByEmail[email]
    return user ? `${user.first_name} ${user.last_name}` : ''
  }

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

  const form = useForm<UsersInvite>({
    // Controlled, so the pills show the normalised (lowercased) emails.
    mode: 'controlled',
    initialValues: { users: [], groups: [], is_intern: true },
    validate: yupResolver(UsersInviteSchema),
    ...input,
  })
  const Controls = controls || undefined
  const [problems, setProblems] = useState<EmailProblem[]>([])
  const [search, setSearch] = useState('')
  const problemCount = problems.reduce((n, p) => n + p.emails.length, 0)

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

  const handleSubmit = (
    values: UsersInvite,
    event: React.FormEvent<HTMLFormElement> | undefined
  ) => {
    event?.stopPropagation()

    if (potentialUserResult.isLoading) {
      form.setFieldError(
        'users',
        'Still loading the Google directory, try again in a moment.'
      )
      return
    }
    if (potentialUserResult.isError) {
      return
    }

    const suffix = `@${workspaceDomain}`
    const found: EmailProblem[] = [
      {
        reason: `Not an ${suffix} address`,
        emails: values.users.filter((e) => !e.endsWith(suffix)),
      },
      {
        reason: 'Not in the Google directory or already has an account',
        emails: values.users.filter(
          (e) => e.endsWith(suffix) && !usersByEmail[e]
        ),
      },
    ]
    if (found.some((p) => p.emails.length > 0)) {
      showProblems(found)
      return
    }

    const mapped = values.users.map((n) => usersByEmail[n]).filter(Boolean)
    onSubmit(form, {
      users: mapped,
      groups: values.groups,
      is_intern: values.is_intern,
    })
  }

  const onValidationFailure = (
    errors,
    values,
    event: React.FormEvent<HTMLFormElement> | undefined
  ) => {
    event?.stopPropagation()
  }

  const usersInputProps = form.getInputProps('users')

  return (
    <form
      autoComplete="off"
      onSubmit={form.onSubmit(handleSubmit, onValidationFailure)}
    >
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
          (potentialUserResult.isError &&
            "Couldn't load the Google directory. Reload the page to try again.")
        }
        key={form.key('users')}
        label="Users"
        placeholder="Enter, select or paste email addresses..."
        data={Object.keys(usersByEmail)}
        filter={filterByNameOrEmail}
        renderOption={renderUserOption}
        searchValue={search}
        onSearchChange={setSearch}
        // Enter picks the highlighted person rather than adding a name as
        // typed. Only while searching, or picking scrolls the list to the top.
        selectFirstOptionOnChange={search !== ''}
        rightSection={
          potentialUserResult.isLoading ? <Loader size="sm" /> : undefined
        }
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
        key={form.key('groups')}
        label="Groups"
        data={groups}
        searchable
        clearable
        size="md"
        mt="md"
      />
      <Checkbox
        {...form.getInputProps('is_intern', { type: 'checkbox' })}
        key={form.key('is_intern')}
        label="Intern"
        size="md"
        mt="md"
      />
      {Controls && (
        <Controls form={form} onSubmit={onSubmit} onCancel={onCancel} />
      )}
    </form>
  )
}
