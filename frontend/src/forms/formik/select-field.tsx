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

  if (!rightSection && (!field.value || !props.clearable)) {
    rightSection = <IconCaretDownFilled size={12} />
  }
  return (
    <Form.Field error={meta.touched && meta.error} required={required}>
      <Select
        {...props}
        size="md"
        onChange={handleChange}
        rightSection={rightSection}
        withCheckIcon={false}
        value={field.value}
      />
      <ErrorMessage name={name} />
    </Form.Field>
  )
}
