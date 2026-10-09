import { NumberInput, Select } from '@mantine/core'
import { DateInput } from '@mantine/dates'
import { useForm, UseFormInput } from '@mantine/form'
import { ServiceCategory, ServiceCreate } from 'api'
import { RichTextToolbarMinimal } from 'comps/rich-text'
import { SERVICE_CATEGORIES } from 'consts'
import dayjs from 'dayjs'
import { RichTextEditorInput } from 'forms/mantine'
import { yupResolver } from 'mantine-form-yup-resolver'
import React, { useState } from 'react'
import { SERVICE_TYPES, ServiceSchema, toServicePayload } from '../schema'

export type ServiceFormType = ReturnType<typeof useForm<ServiceCreate>>

export interface ServiceFormControlProps {
  form: ServiceFormType
  onCancel: () => void
}

export interface ServiceFormProps {
  input: UseFormInput<ServiceCreate>
  onSubmit: (form: ServiceFormType, values: ServiceCreate) => void
  onCancel: () => void
  controls?: React.ComponentType<ServiceFormControlProps>
  /** Show a category select, otherwise the initial category is used. */
  selectCategory?: boolean
}

export const ServiceForm = ({
  input,
  onSubmit,
  onCancel,
  controls,
  selectCategory,
}: ServiceFormProps) => {
  const form = useForm<ServiceCreate>({
    mode: 'uncontrolled',
    validate: yupResolver(ServiceSchema),
    ...input,
  })
  const [category, setCategory] = useState<ServiceCategory | undefined>(
    form.getValues().category
  )

  const Controls = controls || undefined

  const handleSubmit = (
    values: ServiceCreate,
    event: React.FormEvent<HTMLFormElement> | undefined
  ) => {
    event?.stopPropagation()
    onSubmit(form, toServicePayload(values))
  }

  const onValidationFailure = (
    errors,
    values,
    event: React.FormEvent<HTMLFormElement> | undefined
  ) => {
    event?.stopPropagation()
  }

  form.watch('category', ({ value }) => {
    setCategory(value)
    form.setFieldValue('type', undefined!)
    form.setFieldValue('count', value === 'DISCRETE' ? 1 : undefined!)
  })

  return (
    <form
      autoComplete="off"
      onSubmit={form.onSubmit(handleSubmit, onValidationFailure)}
    >
      {selectCategory && (
        <Select
          {...form.getInputProps('category')}
          key={form.key('category')}
          label="Category"
          placeholder="Select the service category"
          size="md"
          mt="md"
          withAsterisk
          data={Object.entries(SERVICE_CATEGORIES).map(([value, label]) => ({
            value,
            label,
          }))}
          withCheckIcon={false}
        />
      )}
      {category && (
        <>
          <Select
            {...form.getInputProps('type')}
            key={form.key('type')}
            label="Type"
            placeholder="Select the service type"
            searchable
            size="md"
            mt="md"
            withAsterisk
            data={Object.entries(SERVICE_TYPES[category]).map(
              ([value, label]) => ({ value, label })
            )}
            withCheckIcon={false}
          />
          <DateInput
            {...form.getInputProps('started_at')}
            key={form.key('started_at')}
            autoComplete="off"
            highlightToday
            locale="en-au"
            label={category === 'DISCRETE' ? 'Date' : 'Start date'}
            placeholder="Select or enter a date"
            size="md"
            mt="md"
            withAsterisk
            valueFormat="DD/MM/YYYY"
            dateParser={(value) =>
              dayjs(value, 'DD/MM/YYYY').format('YYYY-MM-DD')
            }
          />
          {category === 'DISCRETE' ? (
            <NumberInput
              {...form.getInputProps('count')}
              key={form.key('count')}
              autoComplete="off"
              label="Count"
              size="md"
              mt="md"
              withAsterisk
              min={1}
              allowDecimal={false}
              allowNegative={false}
            />
          ) : (
            <DateInput
              {...form.getInputProps('finished_at')}
              key={form.key('finished_at')}
              autoComplete="off"
              clearable
              highlightToday
              locale="en-au"
              label="Finish date"
              placeholder="Select or enter a date"
              size="md"
              mt="md"
              valueFormat="DD/MM/YYYY"
              dateParser={(value) =>
                dayjs(value, 'DD/MM/YYYY').format('YYYY-MM-DD')
              }
            />
          )}
          <RichTextEditorInput
            {...form.getInputProps('notes')}
            key={form.key('notes')}
            label="Notes"
            mt="md"
            toolbar={RichTextToolbarMinimal}
          />
        </>
      )}
      {Controls && <Controls form={form} onCancel={onCancel} />}
    </form>
  )
}
