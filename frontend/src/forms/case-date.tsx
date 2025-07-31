import { Button, Group, Paper, Select, Text, Title } from '@mantine/core'
import { DateInput } from '@mantine/dates'
import { isNotEmpty, useForm } from '@mantine/form'
import { enqueueSnackbar } from 'notistack'
import React from 'react'
import { CaseDetailFormProps } from 'types'
import { getAPIFormErrors } from 'utils'
import dayjs from 'dayjs'
import { RichTextEditorInput } from 'forms/mantine'

import '@mantine/core/styles.css'
import '@mantine/dates/styles.css'

interface FormValues {
  type: string
  date: string
}

export const CaseDateForm = ({ issue, onCancel }: CaseDetailFormProps) => {
  const form = useForm<FormValues>({
    mode: 'uncontrolled',
    initialValues: { type: '', date: null! },
    validate: {
      type: isNotEmpty('required'),
      date: isNotEmpty('required'),
    },
  })

  const handleSubmit = () => {}

  return (
    <Paper withBorder p="md">
      <Title order={3}>Add a critical date</Title>
      <Text mt="md">
        Critical dates are used to track important deadlines related to a case.
      </Text>

      <form onSubmit={form.onSubmit(handleSubmit)}>
        <Select
          {...form.getInputProps('type')}
          key={form.key('type')}
          label="Type"
          searchable
          size="md"
          mt="md"
          data={['Filing Deadline', 'Hearing', 'NTV Termination', 'Other']}
          withCheckIcon={false}
        />
        <DateInput
          {...form.getInputProps('date')}
          key={form.key('date')}
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
    </Paper>
  )
}
