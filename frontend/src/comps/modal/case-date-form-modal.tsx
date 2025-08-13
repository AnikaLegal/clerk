import { Button, Group, Modal, ModalProps } from '@mantine/core'
import { useForm } from '@mantine/form'
import { IssueDateCreate } from 'api'
import {
  CaseDateFields,
  CaseDateFormProvider,
  useCaseDateForm,
} from 'forms/case-date'
import { yupResolver } from 'mantine-form-yup-resolver'
import React from 'react'
import * as Yup from 'yup'

import '@mantine/core/styles.css'

Yup.setLocale({ mixed: { required: 'This field is required.' } })

export const CaseDateSchema: Yup.ObjectSchema<IssueDateCreate> =
  Yup.object().shape({
    issue_id: Yup.string().required(),
    type: Yup.string().required(),
    date: Yup.string().required(),
    notes: Yup.string().optional(),
    is_reviewed: Yup.boolean().optional(),
  })

interface CaseDateFormModalProps extends ModalProps {
  initialValues?: IssueDateCreate
  title: string
  submitButtonLabel: string
  onFormSubmit: (
    form: ReturnType<typeof useForm<IssueDateCreate>>,
    values: IssueDateCreate
  ) => void
}

const CaseDateFormModal = (props: CaseDateFormModalProps) => {
  const form = useCaseDateForm({
    mode: 'uncontrolled',
    initialValues: props.initialValues,
    validate: yupResolver(CaseDateSchema),
  })

  const handleSubmit = (
    values: IssueDateCreate,
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
    form.setValues({})
    props.onClose()
  }

  return (
    <Modal
      opened={props.opened}
      onClose={handleClose}
      size="lg"
      title={props.title}
    >
      <CaseDateFormProvider form={form}>
        <form onSubmit={form.onSubmit(handleSubmit, handleValidationFailure)}>
          <CaseDateFields />
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
      </CaseDateFormProvider>
    </Modal>
  )
}

export default CaseDateFormModal
