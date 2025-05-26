import { Select, SelectProps } from '@mantine/core'
import { ErrorMessage, useField } from 'formik'
import React from 'react'
import { Form } from 'semantic-ui-react'
import { IconCaretDownFilled } from '@tabler/icons-react'

import '@mantine/core/styles.css'

export interface SelectFieldProps extends SelectProps {
  name: string
  label?: string
  required?: boolean
}

export const SelectField = ({
  name,
  label,
  required,
  onChange,
  rightSection,
  ...props
}: SelectFieldProps) => {
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
      <Select
        {...props}
        searchable
        clearable
        size="md"
        styles={{
          input: {
            paddingLeft: 'unset',
            paddingInlineStart: 'var(--input-padding-inline-start)',
          },
        }}
        onChange={handleChange}
        rightSection={
          rightSection ||
          (!field.value && <IconCaretDownFilled size={12} color="black" />)
        }
      />
      <ErrorMessage name={name} />
    </Form.Field>
  )
}
