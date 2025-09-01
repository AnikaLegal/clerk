import { Select } from '@mantine/core'
import { DateInput } from '@mantine/dates'
import { useForm, UseFormInput } from '@mantine/form'
import { IssueDateCreate } from 'api'
import { CASE_DATE_TYPES } from 'consts'
import dayjs from 'dayjs'
import { DateSchema } from 'features/date'
import { RichTextEditorInput } from 'forms/mantine'
import { yupResolver } from 'mantine-form-yup-resolver'
import React from 'react'

import '@mantine/core/styles.css'
import '@mantine/dates/styles.css'

export type DateFormType = ReturnType<typeof useForm<IssueDateCreate>>

export interface DateFormControlProps {
  form: DateFormType
  onSubmit: (form: DateFormType, values: IssueDateCreate) => void
  onCancel: () => void
}

export interface DateFormProps {
  input: UseFormInput<IssueDateCreate>
  onSubmit: (form: DateFormType, values: IssueDateCreate) => void
  onCancel: () => void
  controls?: React.ComponentType<DateFormControlProps>
}

export const DateForm = ({
  input,
  onSubmit,
  onCancel,
  controls,
}: DateFormProps) => {
  const form = useForm<IssueDateCreate>({
    mode: 'uncontrolled',
    validate: yupResolver(DateSchema),
    ...input,
  })
  const Controls = controls || undefined

  const handleSubmit = (
    values: IssueDateCreate,
    event: React.FormEvent<HTMLFormElement> | undefined
  ) => {
    event?.stopPropagation()
    onSubmit(form, values)
  }

  const onValidationFailure = (
    errors,
    values,
    event: React.FormEvent<HTMLFormElement> | undefined
  ) => {
    event?.stopPropagation()
  }

  return (
    <form onSubmit={form.onSubmit(handleSubmit, onValidationFailure)}>
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
      {Controls && (
        <Controls form={form} onSubmit={onSubmit} onCancel={onCancel} />
      )}
    </form>
  )
}
