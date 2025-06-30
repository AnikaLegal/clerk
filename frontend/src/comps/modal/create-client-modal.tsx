import { Button, Group, Modal, ModalProps, TextInput } from '@mantine/core'
import { useForm } from '@mantine/form'
import api, { Client, ClientCreate } from 'api'
import { yupResolver } from 'mantine-form-yup-resolver'
import React, { useState } from 'react'
import { RequiredKeysOf } from 'type-fest'
import { getAPIFormErrors } from 'utils'
import * as Yup from 'yup'

import '@mantine/core/styles.css'

type RequiredClientCreateProps = Pick<
  ClientCreate,
  RequiredKeysOf<ClientCreate>
>

interface CreateClientModalProps extends ModalProps {
  onSuccess: (
    form: ReturnType<typeof useForm<RequiredClientCreateProps>>,
    instance: Client
  ) => void
  onFailure: (
    form: ReturnType<typeof useForm<RequiredClientCreateProps>>,
    exception: any
  ) => void
}

const CreateClientModal = (props: CreateClientModalProps) => {
  const [createClient] = api.useCreateClientMutation()
  const [isClosing, setIsClosing] = useState(false)

  const form = useForm<RequiredClientCreateProps>({
    mode: 'controlled',
    validateInputOnBlur: !isClosing,
    initialValues: {
      first_name: '',
      last_name: '',
      email: '',
    },
    validate: yupResolver(
      Yup.object({
        first_name: Yup.string().required(),
        last_name: Yup.string().required(),
        email: Yup.string()
          .email()
          .matches(
            /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
            'Please enter a valid email address'
          )
          .required(),
      })
    ),
  })

  const handleSubmit = (
    values: RequiredClientCreateProps,
    event: React.FormEvent<HTMLFormElement> | undefined
  ) => {
    event?.stopPropagation()

    form.setSubmitting(true)
    createClient({ clientCreate: values })
      .unwrap()
      .then((instance) => {
        props.onSuccess(form, instance)
      })
      .catch((e) => {
        const errors = getAPIFormErrors(e)
        if (errors) {
          form.setErrors(errors)
        }
        props.onFailure(form, e)
      })
      .finally(() => {
        form.setSubmitting(false)
      })
  }

  const handleClose = () => {
    form.reset()
    props.onClose()
    setIsClosing(false)
  }

  return (
    <Modal
      opened={props.opened}
      onClose={handleClose}
      size="lg"
      title="Create a new client"
    >
      <form onSubmit={form.onSubmit(handleSubmit)}>
        <TextInput
          {...form.getInputProps('first_name')}
          key={form.key('first_name')}
          label="First name"
          size="md"
          data-autofocus
        />
        <TextInput
          {...form.getInputProps('last_name')}
          key={form.key('last_name')}
          label="Last name"
          size="md"
          mt="md"
        />
        <TextInput
          {...form.getInputProps('email')}
          key={form.key('email')}
          label="Email"
          type="email"
          size="md"
          mt="md"
          placeholder="name@example.com"
        />
        <Group justify="right" mt="lg">
          <Button
            variant="default"
            onMouseDown={() => setIsClosing(true)}
            onClick={handleClose}
            disabled={form.submitting}
          >
            Close
          </Button>
          <Button
            type="submit"
            disabled={form.submitting || !form.isValid()}
            loading={form.submitting}
          >
            Create client
          </Button>
        </Group>
      </form>
    </Modal>
  )
}

export default CreateClientModal
