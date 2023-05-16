// Form framework
import React from 'react'
import { DateInput } from 'semantic-ui-calendar-react'
import {
  Button,
  Input,
  Form,
  Dropdown,
  InputOnChangeData,
} from 'semantic-ui-react'
import { MarkdownTextArea } from 'comps/markdown-editor'

import * as Yup from 'yup'
import { FormikProps } from 'formik'

export const FIELD_TYPES = {
  TEXT: 'TEXT',
  NUMBER: 'NUMBER',
  EMAIL: 'EMAIL',
  TEXTAREA: 'TEXTAREA',
  DATE: 'DATE',
  SINGLE_CHOICE: 'SINGLE_CHOICE',
  MULTI_CHOICE: 'MULTI_CHOICE',
  BOOL: 'BOOL',
} as const

export type FormField = {
  label: string
  name: string
  type: (typeof FIELD_TYPES)[keyof typeof FIELD_TYPES]
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

type Model = {
  [fieldName: string]: any
}

type Choices = {
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

export const FormErrors = ({ errors, touched, labels }) => (
  <>
    {Object.entries(errors)
      .filter(([k, v]) => touched[k])
      .map(([k, v]) => (
        <div key={k} className="ui error message">
          <div className="header">{labels ? labels[k] : k}</div>
          <p>{typeof v === 'object' ? Object.values(v) : v}</p>
        </div>
      ))}
  </>
)

interface AutoFormProps {
  fields: FormField[]
  choices: Choices
  formik: FormikProps<{
    [fieldName: string]: string
  }>
  onCancel: any
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

interface FieldComponentProps {
  name: string
  placeholder?: string
  value: string
  handleChange: (
    event: React.ChangeEvent<HTMLInputElement>,
    data: InputOnChangeData
  ) => void
  setFieldValue: (field: string, value: any, shouldValidate?: boolean) => void
  isSubmitting: boolean
}

const TextField = ({
  name,
  placeholder,
  value,
  handleChange,
  isSubmitting,
  type,
}: FieldComponentProps & { type: string }) => (
  <Input
    placeholder={placeholder}
    value={value}
    name={name}
    onChange={handleChange}
    disabled={isSubmitting}
    type={type}
  />
)

const NumberField = ({
  name,
  placeholder,
  value,
  setFieldValue,
  isSubmitting,
}: FieldComponentProps) => {
  return (
    <Input
      placeholder={placeholder}
      value={value || ''}
      name={name}
      onChange={(e, { name, value }) =>
        setFieldValue(name, value === '' ? null : value, false)
      }
      disabled={isSubmitting}
      type="text"
    />
  )
}

const DateField = ({
  name,
  placeholder,
  value,
  setFieldValue,
  isSubmitting,
}: FieldComponentProps) => (
  <DateInput
    placeholder={placeholder}
    value={value}
    name={name}
    dateFormat="DD/MM/YYYY"
    disabled={isSubmitting}
    autoComplete="off"
    onChange={(e, { name, value }) => setFieldValue(name, value, false)}
  />
)

const ChoiceField =
  (multiple: boolean) =>
  ({
    name,
    placeholder,
    value,
    choices,
    setFieldValue,
    isSubmitting,
  }: FieldComponentProps & { choices: [string, string][] }) =>
    (
      <Dropdown
        fluid
        selection
        multiple={multiple}
        value={value}
        style={{ margin: '1em 0' }}
        placeholder={placeholder}
        disabled={isSubmitting}
        options={choices.map(([value, label]) => ({
          key: value,
          value: value,
          text: label,
        }))}
        onChange={(e, { value }) => setFieldValue(name, value, true)}
      />
    )

const BoolField = ({
  name,
  placeholder,
  value,
  setFieldValue,
  isSubmitting,
}: FieldComponentProps) => (
  <Dropdown
    fluid
    selection
    value={value}
    style={{ margin: '1em 0' }}
    loading={isSubmitting}
    placeholder={placeholder}
    options={[
      {
        key: 'Yes',
        text: 'Yes',
        value: true,
      },
      {
        key: 'No',
        text: 'No',
        value: false,
      },
    ]}
    onChange={(e, { value }) => setFieldValue(name, value, false)}
  />
)

const TextAreaField = ({
  name,
  placeholder,
  value,
  handleChange,
  isSubmitting,
}: FieldComponentProps) => (
  <MarkdownTextArea
    name={name}
    value={value}
    placeholder={placeholder}
    onChange={handleChange}
    disabled={isSubmitting}
  />
)

const FIELD_COMPONENTS = {
  TEXT: (props: FieldComponentProps) => <TextField {...props} type="text" />,
  NUMBER: (props: FieldComponentProps) => <NumberField {...props} />,
  EMAIL: (props: FieldComponentProps) => <TextField {...props} type="email" />,
  TEXTAREA: TextAreaField,
  DATE: DateField,
  BOOL: BoolField,
  SINGLE_CHOICE: ChoiceField(false),
  MULTI_CHOICE: ChoiceField(true),
}
