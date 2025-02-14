import { ErrorMessage, useField } from 'formik'
import React from 'react'
import { Form, Input, InputProps } from 'semantic-ui-react'

export interface InputFieldProps extends InputProps {
  name: string
  label?: string
  required?: boolean
}

export const InputField = ({
  name,
  label,
  required,
  ...props
}: InputFieldProps) => {
  const [field, meta] = useField(name)

  return (
    <Form.Field error={meta.touched && meta.error} required={required}>
      {label && <label>{label}</label>}
      <Input {...field} {...props} />
      <ErrorMessage name={name} />
    </Form.Field>
  )
}
