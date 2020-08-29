// @flow
import React from 'react'

import { format } from 'utils'

import { TextEl } from './text'

export const NumberInput = ({ value, onChange, ...props }: any) => {
  return (
    <TextEl
      type="text"
      inputMode="numeric"
      value={format.integer.toString(value)}
      onChange={(e) => onChange(format.integer.toValue(e.target.value))}
      {...props}
    />
  )
}
