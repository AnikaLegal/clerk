// Form framework
import React from 'react'
import { Button, Form } from 'semantic-ui-react'

import * as Yup from 'yup'
import { FormikProps } from 'formik'
import {
  FIELD_COMPONENTS,
  FIELD_TYPES,
  FieldComponentType,
} from './field-component'

export type FormField = {
  label: string
  name: string
  type: FieldComponentType
  placeholder?: string
  schema?: Yup.AnySchema
}

const FieldSchema = Yup.array().of(
  Yup.object().shape({
    label: Yup.string().required(),
    name: Yup.string().required(),
    type: Yup.string().oneOf(Object.values(FIELD_TYPES)).required(),
    placeholder: Yup.string(),
    schema: Yup.object(),
  })
)

export const getFormSchema = (formFields: FormField[]) =>
  Yup.object().shape(
    formFields.reduce(
      (acc, val) =>
        val.schema
          ? {
              ...acc,
              [val.name]: val.schema,
            }
          : acc,
      {}
    )
  )

export type Model = {
  [fieldName: string]: any
}

export type Choices = {
  [fieldName: string]: [string, string][]
}

export const getModelChoices = (formFields: FormField[], model: Model) =>
  formFields.reduce<Choices>((acc, field) => {
    const fieldVal = model[field.name]
    if (fieldVal && fieldVal.choices) {
      return { ...acc, [field.name]: fieldVal.choices }
    } else {
      return acc
    }
  }, {})

export const getModelInitialValues = (formFields: FormField[], model: Model) =>
  formFields.reduce<{
    [fieldName: string]: string
  }>((acc, field) => {
    const fieldVal = model[field.name]
    const value = fieldVal?.value ?? fieldVal ?? null
    return { ...acc, [field.name]: value }
  }, {})

interface FormErrorsProps {
  errors: any
  touched: any
  labels?: any
}

export const FormErrors: React.FC<FormErrorsProps> = ({
  errors,
  touched,
  labels,
}) => (
  <>
    {Object.entries(errors)
      .filter(([k, v]) => touched[k])
      .map(([k, v]) => (
        <div key={k} className="ui error message">
          <div className="header">{labels ? labels[k] : k}</div>
          <p>{typeof v === 'object' ? Object.values(v) : v as string}</p>
        </div>
      ))}
  </>
)

interface AutoFormProps {
  fields: FormField[]
  choices: Choices
  formik: FormikProps<{
    [fieldName: string]: unknown
  }>
  onCancel?: null | (() => void)
  submitText?: string
  cancelText?: string
}

export const AutoForm = ({
  fields,
  choices,
  formik: {
    values,
    errors,
    touched,
    handleChange,
    handleSubmit,
    isSubmitting,
    setFieldValue,
  },
  onCancel = null,
  submitText = 'Submit',
  cancelText = 'Cancel',
}: AutoFormProps) => {
  FieldSchema.validateSync(fields)
  const labels = fields.reduce((acc, f) => ({ ...acc, [f.name]: f.label }), {})
  return (
    <Form onSubmit={handleSubmit} error={Object.keys(errors).length > 0}>
      {fields.map((f) => {
        const FieldComponent = FIELD_COMPONENTS[f.type]
        return (
          <Form.Field key={f.name} error={touched[f.name] && !!errors[f.name]}>
            <label>{f.label}</label>
            <FieldComponent
              {...f}
              value={values[f.name]}
              handleChange={handleChange}
              isSubmitting={isSubmitting}
              setFieldValue={setFieldValue}
              choices={choices[f.name]}
            />
          </Form.Field>
        )
      })}
      <FormErrors errors={errors} labels={labels} touched={touched} />
      <Button
        primary
        type="submit"
        disabled={isSubmitting}
        loading={isSubmitting}
      >
        {submitText}
      </Button>
      {onCancel && (
        <Button
          disabled={isSubmitting}
          onClick={(e) => {
            e.preventDefault()
            onCancel()
          }}
        >
          {cancelText}
        </Button>
      )}
    </Form>
  )
}
