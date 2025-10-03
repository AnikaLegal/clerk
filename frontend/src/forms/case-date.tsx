import { Button, Group, Paper, Text, Title } from '@mantine/core'
import api, {
  IssueDateCreate,
  useAppDispatch,
  useCreateCaseDateMutation,
} from 'api'
import { DateForm, DateFormControlProps, DateFormType } from 'features/date'
import { enqueueSnackbar } from 'notistack'
import React from 'react'
import { CaseDetailFormProps } from 'types'
import { getAPIErrorMessage, getAPIFormErrors } from 'utils'

export const CaseDateForm = ({ issue, onCancel }: CaseDetailFormProps) => {
  const [createDate] = useCreateCaseDateMutation()
  const dispatch = useAppDispatch()

  const initialValues: IssueDateCreate = {
    type: undefined!,
    date: undefined!,
    issue_id: issue.id,
  }

  const handleSubmit = (form: DateFormType, values: IssueDateCreate) => {
    form.setSubmitting(true)
    createDate({
      issueDateCreate: values,
    })
      .unwrap()
      .then((date) => {
        enqueueSnackbar('Critical date created', { variant: 'success' })
        dispatch(api.util.invalidateTags(['CASE']))
      })
      .catch((e) => {
        enqueueSnackbar(
          getAPIErrorMessage(e, 'Failed to create critical date'),
          {
            variant: 'error',
          }
        )
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
      <Title order={3}>Add a critical date</Title>
      <Text mt="md">
        Critical dates are used to track important deadlines related to a case.
      </Text>
      <DateForm
        input={{
          initialValues: initialValues,
        }}
        onSubmit={handleSubmit}
        onCancel={onCancel}
        controls={CaseDateFormControls}
      />
    </Paper>
  )
}

const CaseDateFormControls = ({ form, onCancel }: DateFormControlProps) => {
  return (
    <Group mt="lg">
      <Button
        type="submit"
        disabled={form.submitting}
        loading={form.submitting}
        color="green"
        size="md"
      >
        Add critical date
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
}
