import { Button, Group } from '@mantine/core'
import { useDisclosure } from '@mantine/hooks'
import { IconCheck } from '@tabler/icons-react'
import {
  IssueDate,
  IssueDateCreate,
  useDeleteCaseDateMutation,
  useUpdateCaseDateMutation,
} from 'api'
import {
  ActionIconWithConfirmation,
  DeleteActionIconWithConfirmation,
  UpdateActionIcon,
} from 'comps/action-icon'
import dayjs from 'dayjs'
import customParseFormat from 'dayjs/plugin/customParseFormat'
import {
  DateFormControlProps,
  DateFormModal,
  DateFormType,
} from 'features/date'
import { enqueueSnackbar } from 'notistack'
import React from 'react'
import { getAPIErrorMessage } from 'utils'

import '@mantine/core/styles.css'

dayjs.extend(customParseFormat)

interface DateActionIconGroupProps {
  date: IssueDate
}

const DateActionIconGroup = ({ date }: DateActionIconGroupProps) => {
  const [deleteCaseDate] = useDeleteCaseDateMutation()
  const [updateCaseDate] = useUpdateCaseDateMutation()
  const [isUpdateModalOpen, updateModalHandler] = useDisclosure(false)

  const initialValues: IssueDateCreate = {
    issue_id: date.issue.id,
    type: date.type,
    date: dayjs(date.date, 'DD/MM/YYYY').format('YYYY-MM-DD'),
    notes: date.notes,
  }

  const handleDelete = () => {
    deleteCaseDate({ id: date.id })
      .unwrap()
      .then(() => {
        enqueueSnackbar('Critical date deleted', { variant: 'success' })
      })
      .catch((e) => {
        enqueueSnackbar(
          getAPIErrorMessage(e, 'Failed to delete critical date'),
          {
            variant: 'error',
          }
        )
      })
  }

  const handleReviewed = () => {
    updateCaseDate({
      id: date.id,
      issueDateCreate: {
        ...initialValues,
        is_reviewed: !date.is_reviewed,
      },
    })
      .unwrap()
      .then(() => {
        enqueueSnackbar('Critical date updated', { variant: 'success' })
      })
      .catch((e) => {
        enqueueSnackbar(
          getAPIErrorMessage(e, 'Failed to update critical date'),
          {
            variant: 'error',
          }
        )
      })
  }

  const handleUpdate = (form: DateFormType, values: IssueDateCreate) => {
    form.setSubmitting(true)
    updateCaseDate({
      id: date.id,
      issueDateCreate: values,
    })
      .unwrap()
      .then(() => {
        enqueueSnackbar('Critical date updated', { variant: 'success' })
        updateModalHandler.close()
      })
      .catch((e) => {
        enqueueSnackbar(
          getAPIErrorMessage(e, 'Failed to update critical date'),
          {
            variant: 'error',
          }
        )
      })
      .finally(() => {
        form.setSubmitting(false)
        form.setValues({})
      })
  }

  return (
    <>
      <DateFormModal
        input={{ initialValues: initialValues }}
        modal={{
          opened: isUpdateModalOpen,
          title: 'Update critical date',
        }}
        onSubmit={handleUpdate}
        onCancel={() => updateModalHandler.close()}
        controls={ModalDateFormControls}
      />
      <ActionIconWithConfirmation.Group>
        <ActionIconWithConfirmation
          tooltip={{ label: 'Toggle reviewed' }}
          icon={<IconCheck stroke={1.5} />}
          onClick={handleReviewed}
          confirmButton={{
            label: date.is_reviewed
              ? 'Confirm not reviewed'
              : 'Confirm reviewed',
          }}
        />
        <UpdateActionIcon onClick={() => updateModalHandler.open()} />
        <DeleteActionIconWithConfirmation
          onClick={handleDelete}
          confirmButton={{
            label: 'Confirm delete',
            color: 'red',
          }}
        />
      </ActionIconWithConfirmation.Group>
    </>
  )
}

const ModalDateFormControls = ({ form, onCancel }: DateFormControlProps) => {
  return (
    <Group justify="right" mt="lg">
      <Button
        variant="default"
        onClick={onCancel}
        disabled={form.submitting}
        size="md"
      >
        Close
      </Button>
      <Button
        type="submit"
        disabled={form.submitting}
        loading={form.submitting}
        size="md"
      >
        Update critical date
      </Button>
    </Group>
  )
}

export default DateActionIconGroup
