import { Select } from '@mantine/core'
import { DateInput } from '@mantine/dates'
import { useForm, UseFormInput } from '@mantine/form'
import { IssueDateCreate } from 'api'
import { RichTextToolbarMinimal } from 'comps/rich-text'
import { CASE_DATE_HEARING_TYPES, CASE_DATE_TYPES } from 'consts'
import dayjs from 'dayjs'
import { DateSchema } from 'features/date/schema'
import { RichTextAreaInput, RichTextEditorInput } from 'forms/mantine'
import { yupResolver } from 'mantine-form-yup-resolver'
import React, { useState } from 'react'

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
  const [isHearing, setIsHearing] = useState(
    form.values.type == 'HEARING_LISTED'
  )

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

  form.watch('type', ({ value }) => {
    setIsHearing(value == 'HEARING_LISTED')
    form.setFieldValue('hearing_type', undefined)
    form.setFieldValue('hearing_location', undefined)
  })

  return (
    <form onSubmit={form.onSubmit(handleSubmit, onValidationFailure)}>
      <DateInput
        {...form.getInputProps('date')}
        key={form.key('date')}
        clearable
        highlightToday
        locale="en-au"
        label="Date"
        size="md"
        mt="md"
        placeholder="Select or enter a date"
        valueFormat="DD/MM/YYYY"
        dateParser={(value) => dayjs(value, 'DD/MM/YYYY').format('YYYY-MM-DD')}
        minDate={dayjs().format('YYYY-MM-DD')}
      />
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
      {isHearing && (
        <>
          <Select
            {...form.getInputProps('hearing_type')}
            key={form.key('hearing_type')}
            clearable
            label="Hearing type"
            searchable
            size="md"
            mt="md"
            data={Object.entries(CASE_DATE_HEARING_TYPES).map(
              ([value, label]) => ({
                value,
                label,
              })
            )}
            withCheckIcon={false}
          />
          <RichTextAreaInput
            {...form.getInputProps('hearing_location')}
            key={form.key('Hearing location')}
            label="Hearing location"
            mt="md"
          />
        </>
      )}
      <RichTextEditorInput
        {...form.getInputProps('notes')}
        key={form.key('notes')}
        label="Notes"
        mt="md"
        toolbar={RichTextToolbarMinimal}
      />
      {Controls && (
        <Controls form={form} onSubmit={onSubmit} onCancel={onCancel} />
      )}
    </form>
  )
}
