import { ErrorMessage, useField } from 'formik'
import React from 'react'
import { Form } from 'semantic-ui-react'
import DateInput from 'comps/date-input'
import { DateInputProps } from 'comps/date-input'

export interface DateInputFieldProps
  extends Omit<DateInputProps, 'value' | 'onChange'> {
  name: string
  label: string
  required?: boolean
}

export const DateInputField = ({
  name,
  label,
  required,
  ...props
}: DateInputFieldProps) => {
  const [field, meta, helpers] = useField(name)

  const handleBlur = (e) => {
    if (props.onBlur) {
      props.onBlur(e)
    }
  }
  const handleChange = (e, data) => {
    helpers.setValue(data.value)
    if (props.onChange) {
      props.onChange(e, data)
    }
  }

  return (
    <Form.Field error={meta.touched && meta.error} required={required}>
      <label>{label}</label>
      <DateInput
        {...field}
        {...props}
        onBlur={handleBlur}
        onChange={handleChange}
        autoComplete="off"
      />
      <ErrorMessage name={name} />
    </Form.Field>
  )
}
