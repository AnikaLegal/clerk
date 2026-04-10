import { Loader, MultiSelect, TagsInput } from '@mantine/core'
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
  onSubmit: (form: InviteFormType, values: UsersCreate) => void
  onCancel: () => void
  input?: UseFormInput<UsersInvite>
  controls?: React.ComponentType<InviteFormControlProps>
}

export const InviteForm = ({
  groups,
  onSubmit,
  onCancel,
  input,
  controls,
}: InviteFormProps) => {
  const potentialUserResult = useGetPotentialUsersQuery()
  const usersByEmail = Object.fromEntries(
    potentialUserResult.data?.map((user) => [user.email, user]) || []
  )
  const form = useForm<UsersInvite>({
    mode: 'uncontrolled',
    validate: yupResolver(UsersInviteSchema),
    ...input,
  })
  const Controls = controls || undefined

  const handleSubmit = (
    values: UsersInvite,
    event: React.FormEvent<HTMLFormElement> | undefined
  ) => {
    event?.stopPropagation()

    const notFound = values.users.filter((e) => !usersByEmail[e])
    if (notFound.length > 0) {
      form.setFieldError(
        'users',
        `User${notFound.length > 1 ? 's' : ''} not found: ${notFound.join(', ')}`
      )
      return
    }

    const mapped = values.users.map((n) => usersByEmail[n]).filter(Boolean)
    onSubmit(form, { users: mapped, groups: values.groups })
  }

  const onValidationFailure = (
    errors,
    values,
    event: React.FormEvent<HTMLFormElement> | undefined
  ) => {
    event?.stopPropagation()
  }

  return (
    <form onSubmit={form.onSubmit(handleSubmit, onValidationFailure)}>
      <TagsInput
        {...form.getInputProps('users')}
        key={form.key('users')}
        label="Users"
        placeholder="Enter, select or paste email addresses..."
        data={Object.keys(usersByEmail)}
        disabled={potentialUserResult.isLoading}
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
      {Controls && (
        <Controls form={form} onSubmit={onSubmit} onCancel={onCancel} />
      )}
    </form>
  )
}
