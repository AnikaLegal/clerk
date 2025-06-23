import { Button, Group, Modal, ModalProps, TextInput } from '@mantine/core'
import { useForm } from '@mantine/form'
import api, { Client, ClientCreate } from 'api'
import { yupResolver } from 'mantine-form-yup-resolver'
import React from 'react'
import { RequiredProps } from 'utils'
import * as Yup from 'yup'

import '@mantine/core/styles.css'

type RequiredClientCreateProps = RequiredProps<ClientCreate>

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

  const form = useForm<RequiredClientCreateProps>({
    mode: 'controlled',
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
          .matches(/^[^\s@]+@[^\s@]+\.[^\s@]+$/)
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
        props.onFailure(form, e)
      })
      .finally(() => {
        form.setSubmitting(false)
      })
  }

  return (
    <Modal
      opened={props.opened}
      onClose={props.onClose}
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
        />
        <Group justify="right" mt="lg">
          <Button
            variant="default"
            onClick={props.onClose}
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
