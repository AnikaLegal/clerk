import { SelectSearch, SelectSearchProps } from 'comps/select-search'
import { ErrorMessage, useField } from 'formik'
import React from 'react'
import { Form } from 'semantic-ui-react'

export interface SelectSearchFieldProps extends SelectSearchProps {
  name: string
  label?: string
  required?: boolean
}

export const SelectSearchField = ({
  name,
  label,
  required,
  onChange,
  ...props
}: SelectSearchFieldProps) => {
  const [field, meta, helpers] = useField(name)
  const handleChange = (value, option) => {
    helpers.setValue(value)
    if (onChange) {
      onChange(value, option)
    }
  }
  return (
    <Form.Field error={meta.touched && meta.error} required={required}>
      {label && <label>{label}</label>}
      <SelectSearch onChange={handleChange} {...props} />
      <ErrorMessage name={name} />
    </Form.Field>
  )
}
