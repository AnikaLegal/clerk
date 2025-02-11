import React from 'react'
import { DropdownField, DropdownFieldProps } from './dropdown-field'
import { DropdownItemProps } from 'semantic-ui-react'

export interface BooleanFieldProps extends Omit<DropdownFieldProps, 'options'> {
  name: string
  label: string
  required?: boolean
}

export const BooleanField = ({ name, label, ...props }: BooleanFieldProps) => {
  const options: DropdownItemProps[] = [
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
  ]
  return (
    <DropdownField name={name} label={label} options={options} {...props} />
  )
}
