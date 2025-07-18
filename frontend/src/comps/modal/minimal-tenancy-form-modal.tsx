import { Button, Group, Modal, ModalProps, TextInput } from '@mantine/core'
import { useForm } from '@mantine/form'
import { TenancyCreate } from 'api'
import { yupResolver } from 'mantine-form-yup-resolver'
import React from 'react'
import { RequiredKeysOf } from 'type-fest'
import * as Yup from 'yup'

import '@mantine/core/styles.css'

Yup.setLocale({ mixed: { required: 'This field is required.' } })

export type RequiredTenancyProps = Pick<
  TenancyCreate,
  RequiredKeysOf<TenancyCreate>
>

export const RequiredTenancySchema: Yup.ObjectSchema<RequiredTenancyProps> =
  Yup.object().shape({
    address: Yup.string().required(),
    suburb: Yup.string().required(),
    postcode: Yup.string()
      .matches(/^\d{4}$/, 'Please enter a 4-digit number')
      .required(),
  })

interface MinimalTenancyFormModalProps extends ModalProps {
  title: string
  submitButtonLabel: string
  onFormSubmit: (
    form: ReturnType<typeof useForm<RequiredTenancyProps>>,
    values: RequiredTenancyProps
  ) => void
}

const MinimalTenancyFormModal = (props: MinimalTenancyFormModalProps) => {
  const form = useForm<RequiredTenancyProps>({
    mode: 'controlled',
    initialValues: {
      address: '',
      suburb: '',
      postcode: '',
    },
    validate: yupResolver(RequiredTenancySchema),
  })

  const handleSubmit = (
    values: RequiredTenancyProps,
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
          {...form.getInputProps('address')}
          key={form.key('address')}
          label="Address"
          size="md"
          placeholder="123 Main Street"
          data-autofocus
        />
        <TextInput
          {...form.getInputProps('suburb')}
          key={form.key('suburb')}
          label="Suburb"
          size="md"
          mt="md"
          placeholder="Collingwood"
        />
        <TextInput
          {...form.getInputProps('postcode')}
          key={form.key('postcode')}
          label="Postcode"
          size="md"
          mt="md"
          placeholder="1234"
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

export default MinimalTenancyFormModal
