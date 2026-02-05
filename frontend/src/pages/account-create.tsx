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
import { getAPIErrorMessage, getAPIFormErrors, mount } from 'utils'

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
        },
      }).unwrap()
    )
    Promise.allSettled(promises)
      .then((results) => {
        results.forEach((result, index) => {
          if (result.status === 'fulfilled') {
            showNotification({
              type: 'success',
              title: 'User created',
              message: `Invitation sent to ${result.value.email}.`,
              link: {
                text: 'View user',
                url: result.value.url,
              },
              autoClose: 6000,
            })
          } else {
            const email = values.users[index].email
            showNotification({
              type: 'error',
              title: `Failed to create user ${email}`,
              message: getAPIErrorMessage(result.reason),
              autoClose: 6000,
            })
            const requestErrors = getAPIFormErrors(result.reason)
            if (requestErrors) {
              form.setErrors(requestErrors)
            }
          }
        })
        if (results.every((result) => result.status === 'fulfilled')) {
          form.reset()
        }
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
        onSubmit={handleSubmit}
        onCancel={() => {
          /* Do nothing */
        }}
        controls={InviteFormControls}
      />
    </Container>
  )
}

const InviteFormControls = ({ form, onCancel }: InviteFormControlProps) => {
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
