import { Button, Group, Modal, ModalProps, TextInput } from '@mantine/core'
import { useForm } from '@mantine/form'
import api, { Tenancy, TenancyCreate } from 'api'
import { yupResolver } from 'mantine-form-yup-resolver'
import React from 'react'
import { RequiredKeysOf } from 'type-fest'
import { getAPIFormErrors } from 'utils'
import * as Yup from 'yup'

import '@mantine/core/styles.css'

type RequiredTenancyCreateProps = Pick<
  TenancyCreate,
  RequiredKeysOf<TenancyCreate>
>

interface CreateTenancyModalProps extends ModalProps {
  onSuccess: (
    form: ReturnType<typeof useForm<RequiredTenancyCreateProps>>,
    instance: Tenancy
  ) => void
  onFailure: (
    form: ReturnType<typeof useForm<RequiredTenancyCreateProps>>,
    exception: any
  ) => void
}

Yup.setLocale({ mixed: { required: 'This field is required.' } })

const CreateTenancyModal = (props: CreateTenancyModalProps) => {
  const [createTenancy] = api.useCreateTenancyMutation()

  const form = useForm<RequiredTenancyCreateProps>({
    mode: 'controlled',
    initialValues: {
      address: '',
      suburb: '',
      postcode: '',
    },
    validate: yupResolver(
      Yup.object({
        address: Yup.string().required(),
        suburb: Yup.string().required(),
        postcode: Yup.string()
          .matches(/^\d{4}$/, 'Please enter a 4-digit number')
          .required(),
      })
    ),
  })

  const handleSubmit = (
    values: RequiredTenancyCreateProps,
    event: React.FormEvent<HTMLFormElement> | undefined
  ) => {
    event?.stopPropagation()

    form.setSubmitting(true)
    createTenancy({ tenancyCreate: values })
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
      title="Create a new tenancy"
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
            Create tenancy
          </Button>
        </Group>
      </form>
    </Modal>
  )
}

export default CreateTenancyModal
