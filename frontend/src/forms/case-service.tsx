import { Button, Group, Paper, Text, Title } from '@mantine/core'
import api, {
  ServiceCreate,
  useAppDispatch,
  useCreateCaseServiceMutation,
} from 'api'
import {
  ServiceForm as ServiceFormFields,
  ServiceFormControlProps,
  ServiceFormType,
} from 'features/service'
import { enqueueSnackbar } from 'notistack'
import React from 'react'
import { CaseDetailFormProps } from 'types'
import { filterEmpty, getAPIErrorMessage, getAPIFormErrors } from 'utils'

export const ServiceForm = ({ issue, onCancel }: CaseDetailFormProps) => {
  const [createService] = useCreateCaseServiceMutation()
  const dispatch = useAppDispatch()

  const initialValues: ServiceCreate = {
    category: undefined!,
    type: undefined!,
    started_at: undefined!,
    finished_at: null,
    count: undefined!,
    notes: null,
  }

  const handleSubmit = (form: ServiceFormType, values: ServiceCreate) => {
    form.setSubmitting(true)
    createService({ id: issue.id, serviceCreate: filterEmpty(values) })
      .unwrap()
      .then(() => {
        /* Invalidate the case tag so that the file note that is created when a
         * service is created is displayed on the timeline */
        dispatch(api.util.invalidateTags(['CASE']))
        enqueueSnackbar('Service created', { variant: 'success' })
      })
      .catch((e) => {
        enqueueSnackbar(getAPIErrorMessage(e, 'Failed to create service'), {
          variant: 'error',
        })
        const requestErrors = getAPIFormErrors(e)
        if (requestErrors) {
          form.setErrors(requestErrors)
        }
      })
      .finally(() => {
        form.setSubmitting(false)
      })
  }

  return (
    <Paper withBorder p="md">
      <Title order={3}>Add a service</Title>
      <Text mt="md">
        Record a unit of work to facilitate the collection of consistent and
        comparable data.
      </Text>
      <ServiceFormFields
        input={{ initialValues }}
        onSubmit={handleSubmit}
        onCancel={onCancel}
        controls={ServiceFormControls}
        selectCategory
      />
    </Paper>
  )
}

const ServiceFormControls = ({ form, onCancel }: ServiceFormControlProps) => (
  <Group mt="lg">
    <Button
      type="submit"
      disabled={form.submitting}
      loading={form.submitting}
      color="green"
      size="md"
    >
      Create service
    </Button>
    <Button
      variant="default"
      onClick={onCancel}
      disabled={form.submitting}
      size="md"
    >
      Close
    </Button>
  </Group>
)
