import { Button, Group, Paper, Select, Text, Title } from '@mantine/core'
import { DateInput } from '@mantine/dates'
import { createFormContext, isNotEmpty } from '@mantine/form'
import api, {
  IssueDateCreate,
  useAppDispatch,
  useCreateCaseDateMutation,
} from 'api'
import { CASE_DATE_TYPES } from 'consts'
import dayjs from 'dayjs'
import { RichTextEditorInput } from 'forms/mantine'
import { enqueueSnackbar } from 'notistack'
import React from 'react'
import { CaseDetailFormProps } from 'types'
import { getAPIErrorMessage, getAPIFormErrors } from 'utils'

import '@mantine/core/styles.css'
import '@mantine/dates/styles.css'

export const [CaseDateFormProvider, useCaseDateFormContext, useCaseDateForm] =
  createFormContext<IssueDateCreate>()

export const CaseDateForm = ({ issue, onCancel }: CaseDetailFormProps) => {
  const [createDate] = useCreateCaseDateMutation()
  const dispatch = useAppDispatch()

  const form = useCaseDateForm({
    mode: 'uncontrolled',
    initialValues: { type: '', date: '', notes: '', issue_id: issue.id },
    validate: {
      type: isNotEmpty('This field is required.'),
      date: isNotEmpty('This field is required.'),
    },
  })

  const handleSubmit = (values: IssueDateCreate) => {
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

      <CaseDateFormProvider form={form}>
        <form onSubmit={form.onSubmit(handleSubmit)}>
          <CaseDateFields />
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
        </form>
      </CaseDateFormProvider>
    </Paper>
  )
}

export const CaseDateFields = () => {
  const form = useCaseDateFormContext()
  return (
    <>
      <Select
        {...form.getInputProps('type')}
        key={form.key('type')}
        clearable
        label="Type"
        searchable
        size="md"
        mt="md"
        data={Object.entries(CASE_DATE_TYPES).map(([value, label]) => ({
          value,
          label,
        }))}
        withCheckIcon={false}
      />
      <DateInput
        {...form.getInputProps('date')}
        key={form.key('date')}
        clearable
        highlightToday
        locale="en-au"
        label="Date"
        size="md"
        mt="md"
        placeholder="Select a date"
        valueFormat="DD/MM/YYYY"
        dateParser={(value) => dayjs(value, 'DD/MM/YYYY').toDate()}
      />
      <RichTextEditorInput
        {...form.getInputProps('notes')}
        key={form.key('notes')}
        label="Notes"
        mt="md"
        description="If you are logging a hearing date, please note the method of hearing (teleconference/in person) and location."
      />
    </>
  )
}
