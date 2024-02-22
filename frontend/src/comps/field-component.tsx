import React from 'react'
import DateInput from 'comps/date-input'
import { Input, Dropdown, InputOnChangeData } from 'semantic-ui-react'
import { MarkdownTextArea } from 'comps/markdown-editor'

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

export type FieldComponentType = (typeof FIELD_TYPES)[keyof typeof FIELD_TYPES]

interface FieldComponentProps {
  name: string
  placeholder?: string
  value: any
  handleChange: (
    event: React.ChangeEvent<HTMLInputElement>,
    data: InputOnChangeData
  ) => void
  setFieldValue: (field: string, value: any, shouldValidate?: boolean) => void
  isSubmitting: boolean
  choices?: [string, string][]
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
      value={!value && value !== 0 ? '' : value}
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
  }: FieldComponentProps & {
    choices: NonNullable<FieldComponentProps['choices']>
  }) =>
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
    onChange={(_e, { value }) => setFieldValue(name, value, false)}
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

export const FIELD_COMPONENTS: {
  [fieldType in FieldComponentType]: React.FunctionComponent<FieldComponentProps>
} = {
  TEXT: (props: FieldComponentProps) => <TextField {...props} type="text" />,
  NUMBER: (props: FieldComponentProps) => <NumberField {...props} />,
  EMAIL: (props: FieldComponentProps) => <TextField {...props} type="email" />,
  TEXTAREA: TextAreaField,
  DATE: DateField,
  BOOL: BoolField,
  SINGLE_CHOICE: ChoiceField(false),
  MULTI_CHOICE: ChoiceField(true),
} as const
