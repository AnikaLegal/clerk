import { Button, Group, Modal, ModalProps, TextInput } from '@mantine/core'
import { useForm } from '@mantine/form'
import api, { Tenancy, TenancyCreate } from 'api'
import { yupResolver } from 'mantine-form-yup-resolver'
import React, { useEffect, useState } from 'react'
import { getAPIFormErrors, RequiredProps } from 'utils'
import * as Yup from 'yup'

import '@mantine/core/styles.css'
import { useClickOutside } from '@mantine/hooks'

type RequiredTenancyCreateProps = RequiredProps<TenancyCreate>

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
  const [isClosing, setIsClosing] = useState(false)

  const form = useForm<RequiredTenancyCreateProps>({
    mode: 'controlled',
    validateInputOnBlur: !isClosing,
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
      title="Create a new tenancy"
    >
      <form onSubmit={form.onSubmit(handleSubmit)}>
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
          placeholder="Enter the suburb e.g. Collingwood"
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
            Create tenancy
          </Button>
        </Group>
      </form>
    </Modal>
  )
}

export default CreateTenancyModal
