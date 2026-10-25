import { Checkbox, Loader, MultiSelect, TagsInput } from '@mantine/core'
import { useForm, UseFormInput } from '@mantine/form'
import { useGetPotentialUsersQuery } from 'api'
import { UsersCreate, UsersInvite, UsersInviteSchema } from 'features/invite'
import { yupResolver } from 'mantine-form-yup-resolver'
import React from 'react'

export type InviteFormType = ReturnType<typeof useForm<UsersInvite>>

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
  const form = useForm<UsersInvite>({
    mode: 'uncontrolled',
    initialValues: { users: [], groups: [], is_intern: true },
    validate: yupResolver(UsersInviteSchema),
    ...input,
  })
  const Controls = controls || undefined

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
    const external = values.users.filter((e) => !e.endsWith(suffix))
    const notFound = values.users.filter(
      (e) => e.endsWith(suffix) && !usersByEmail[e]
    )
    const errors = [
      external.length > 0 && `Not an ${suffix} address: ${external.join(', ')}`,
      notFound.length > 0 &&
        `Not in the Google directory or already has an account: ${notFound.join(', ')}`,
    ].filter(Boolean)
    if (errors.length > 0) {
      form.setFieldError('users', errors.join('. '))
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
        onChange={(value) =>
          usersInputProps.onChange([
            ...new Set(value.map((e) => e.trim().toLowerCase())),
          ])
        }
        error={
          usersInputProps.error ||
          (potentialUserResult.isError &&
            "Couldn't load the Google directory. Reload the page to try again.")
        }
        key={form.key('users')}
        label="Users"
        placeholder="Enter, select or paste email addresses..."
        data={Object.keys(usersByEmail)}
        rightSection={
          potentialUserResult.isLoading ? <Loader size="sm" /> : undefined
        }
        splitChars={[',', ' ', '|', ';', '\n']}
        clearable
        size="md"
      />
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
