import { Button, Container, Group, Title } from '@mantine/core'
import { useCreateUserMutation } from 'api'
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
  group_values: string[]
  workspace_domain: string
}
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const CONTEXT = (window as any).REACT_CONTEXT as DjangoContext

const App = () => {
  const [createUser] = useCreateUserMutation()

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
        const failed = new Set<string>()
        const failures: string[] = []
        results.forEach((result, index) => {
          const email = values.users[index].email
          if (result.status === 'fulfilled') {
            showNotification({
              type: 'success',
              title: 'User created',
              message: `Invitation sent to ${result.value.email}.`,
              link: {
                text: 'View user',
                url: result.value.url,
              },
              autoClose: 4000,
            })
          } else {
            const message = getAPIErrorMessage(result.reason)
            failed.add(email.toLowerCase())
            failures.push(`${email}: ${message}`)
            showNotification({
              type: 'error',
              title: `Failed to create user ${email}`,
              message,
              autoClose: false,
            })
          }
        })
        if (failures.length === 0) {
          form.reset()
          return
        }
        // Keep only the failed emails so a retry doesn't re-invite the rest.
        form.setFieldValue(
          'users',
          form.getValues().users.filter((email) => failed.has(email))
        )
        form.setFieldError('users', failures.join('. '))
      })
      .finally(() => {
        form.setSubmitting(false)
      })
  }

  return (
    <Container size="xl">
      <Title order={1} mb="md">
        Invite users
      </Title>
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
