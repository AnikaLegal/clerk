import { Group } from '@mantine/core'
import { useDisclosure } from '@mantine/hooks'
import {
  Issue,
  Service,
  ServiceCreate,
  useDeleteCaseServiceMutation,
  useUpdateCaseServiceMutation,
} from 'api'
import {
  ActionIconWithConfirmation,
  DeleteActionIconWithConfirmation,
  UpdateActionIcon,
} from 'comps/action-icon'
import dayjs from 'dayjs'
import customParseFormat from 'dayjs/plugin/customParseFormat'
import { enqueueSnackbar } from 'notistack'
import React from 'react'
import { getAPIErrorMessage, getAPIFormErrors } from 'utils'
import { ServiceFormType } from './service-form'
import { ServiceFormModal } from './service-form-modal'
import { UpdateServiceControls } from './service-modal-controls'

dayjs.extend(customParseFormat)

const toIsoDate = (value: string | null) =>
  value ? dayjs(value, 'DD/MM/YYYY').format('YYYY-MM-DD') : null

interface ServiceActionIconGroupProps {
  issue: Issue
  service: Service
}

export const ServiceActionIconGroup = ({
  issue,
  service,
}: ServiceActionIconGroupProps) => {
  const [deleteService] = useDeleteCaseServiceMutation()
  const [updateService] = useUpdateCaseServiceMutation()
  const [isUpdateModalOpen, updateModalHandler] = useDisclosure(false)

  const initialValues: ServiceCreate = {
    category: service.category,
    type: service.type,
    started_at: toIsoDate(service.started_at)!,
    finished_at: toIsoDate(service.finished_at),
    count: service.count,
    notes: service.notes,
  }

  const handleDelete = () => {
    deleteService({ id: issue.id, serviceId: service.id })
      .unwrap()
      .then(() => {
        enqueueSnackbar('Service deleted', { variant: 'success' })
      })
      .catch((e) => {
        enqueueSnackbar(getAPIErrorMessage(e, 'Failed to delete service'), {
          variant: 'error',
        })
      })
  }

  const handleUpdate = (form: ServiceFormType, values: ServiceCreate) => {
    form.setSubmitting(true)
    updateService({
      id: issue.id,
      serviceId: service.id,
      serviceUpdate: values,
    })
      .unwrap()
      .then(() => {
        enqueueSnackbar('Service updated', { variant: 'success' })
        updateModalHandler.close()
      })
      .catch((e) => {
        enqueueSnackbar(getAPIErrorMessage(e, 'Failed to update service'), {
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
      <ServiceFormModal
        input={{ initialValues }}
        modal={{
          opened: isUpdateModalOpen,
          title: `Update ${service.category.toLowerCase()} service`,
        }}
        onSubmit={handleUpdate}
        onCancel={() => updateModalHandler.close()}
        controls={UpdateServiceControls}
      />
      <Group justify="center" wrap="nowrap">
        <ActionIconWithConfirmation.Group>
          <UpdateActionIcon onClick={() => updateModalHandler.open()} />
          <DeleteActionIconWithConfirmation
            onClick={handleDelete}
            confirmButton={{ label: 'Confirm delete', color: 'red' }}
          />
        </ActionIconWithConfirmation.Group>
      </Group>
    </>
  )
}
