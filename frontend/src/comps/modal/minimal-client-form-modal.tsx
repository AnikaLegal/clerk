import { Button, Group, Modal, ModalProps, TextInput } from '@mantine/core'
import { useForm } from '@mantine/form'
import { ClientCreate } from 'api'
import { yupResolver } from 'mantine-form-yup-resolver'
import React from 'react'
import { RequiredKeysOf } from 'type-fest'
import * as Yup from 'yup'

import '@mantine/core/styles.css'

Yup.setLocale({ mixed: { required: 'This field is required.' } })

export type RequiredClientProps = Pick<
  ClientCreate,
  RequiredKeysOf<ClientCreate>
>

export const RequiredClientSchema: Yup.ObjectSchema<RequiredClientProps> =
  Yup.object().shape({
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

interface MinimalClientFormModalProps extends ModalProps {
  title: string
  submitButtonLabel: string
  onFormSubmit: (
    form: ReturnType<typeof useForm<RequiredClientProps>>,
    values: RequiredClientProps
  ) => void
}

const MinimalClientFormModal = (props: MinimalClientFormModalProps) => {
  const form = useForm<RequiredClientProps>({
    mode: 'controlled',
    initialValues: {
      first_name: '',
      last_name: '',
      email: '',
    },
    validate: yupResolver(RequiredClientSchema),
  })

  const handleSubmit = (
    values: RequiredClientProps,
    event: React.FormEvent<HTMLFormElement> | undefined
  ) => {
    event?.stopPropagation()
    props.onFormSubmit(form, values)
  }

  const handleValidationFailure = (
    errors,
    values,
    event: React.FormEvent<HTMLFormElement> | undefined
  ) => {
    event?.stopPropagation()
  }

  const handleClose = () => {
    form.reset()
    props.onClose()
  }

  return (
    <Modal
      opened={props.opened}
      onClose={handleClose}
      size="lg"
      title={props.title}
    >
      <form onSubmit={form.onSubmit(handleSubmit, handleValidationFailure)}>
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
          size="md"
          mt="md"
          placeholder="name@example.com"
        />
        <Group justify="right" mt="lg">
          <Button
            variant="default"
            onClick={handleClose}
            disabled={form.submitting}
          >
            Close
          </Button>
          <Button
            type="submit"
            disabled={form.submitting}
            loading={form.submitting}
          >
            {props.submitButtonLabel}
          </Button>
        </Group>
      </form>
    </Modal>
  )
}

export default MinimalClientFormModal
