import React from 'react'

import { SelectInput, Form } from 'intake/design'
import { timeout } from 'intake/utils'
import { FormFieldProps } from './types'

export const ChoiceSingleField = ({
  onNext,
  field,
  value,
  onChange,
  children,
}: FormFieldProps) => {
  const onClick = async (val) => {
    onChange(val)
    await timeout(200)
    onNext({ preventDefault: () => {} })
  }

  return (
    <Form.Outer>
      <Form.Content>
        {children}
        <SelectInput value={value} onChange={onClick} options={field.choices} />
      </Form.Content>
    </Form.Outer>
  )
}
