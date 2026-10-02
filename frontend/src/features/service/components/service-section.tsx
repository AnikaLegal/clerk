import { Button, Group, Title } from '@mantine/core'
import { useDisclosure } from '@mantine/hooks'
import {
  Issue,
  ServiceCategory,
  ServiceCreate,
  useCreateCaseServiceMutation,
} from 'api'
import { filterEmpty, getAPIErrorMessage, getAPIFormErrors } from 'utils'
import { enqueueSnackbar } from 'notistack'
import React from 'react'
import { ServiceFormType } from './service-form'
import { ServiceFormModal } from './service-form-modal'
import { AddServiceControls } from './service-modal-controls'
import { ServiceTable } from './service-table'

interface ServiceSectionProps {
  issue: Issue
  category: ServiceCategory
  canChange: boolean
}

export const ServiceSection = ({
  issue,
  category,
  canChange,
}: ServiceSectionProps) => {
  const [isOpen, handler] = useDisclosure(false)
  const [createService] = useCreateCaseServiceMutation()
  const noun = category.toLowerCase()

  const initialValues: ServiceCreate = {
    category,
    type: undefined!,
    started_at: undefined!,
    finished_at: null,
    count: category === 'DISCRETE' ? 1 : undefined!,
    notes: null,
  }

  const handleSubmit = (form: ServiceFormType, values: ServiceCreate) => {
    form.setSubmitting(true)
    createService({ id: issue.id, serviceCreate: filterEmpty(values) })
      .unwrap()
      .then(() => {
        enqueueSnackbar('Service created', { variant: 'success' })
        handler.close()
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
    <>
      <Group justify="space-between" mt="xl">
        <Title order={2}>
          {category === 'DISCRETE' ? 'Discrete' : 'Ongoing'} services
        </Title>
        {canChange && (
          <Button onClick={() => handler.open()}>Add {noun} service</Button>
        )}
      </Group>
      <ServiceFormModal
        input={{ initialValues }}
        modal={{ opened: isOpen, title: `Add ${noun} service` }}
        onSubmit={handleSubmit}
        onCancel={() => handler.close()}
        controls={AddServiceControls}
      />
      <ServiceTable issue={issue} category={category} canChange={canChange} />
    </>
  )
}
