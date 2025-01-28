import { ErrorMessage, useField } from 'formik'
import React from 'react'
import { Dropdown, DropdownProps, Form } from 'semantic-ui-react'

interface DropdownFieldProps extends DropdownProps {
  name: string
  label: string
  required?: boolean
}

export const DropdownField = ({
  name,
  label,
  required,
  ...props
}: DropdownFieldProps) => {
  const [field, meta, helpers] = useField(name)
  const handleChange = (e, data) => {
    helpers.setValue(data.value)
    if (props.onChange) {
      props.onChange(e, data)
    }
  }

  return (
    <Form.Field error={meta.touched && meta.error} required={required}>
      <label>{label}</label>
      <Dropdown fluid selection {...field} {...props} onChange={handleChange} />
      <ErrorMessage name={name} />
    </Form.Field>
  )
}
