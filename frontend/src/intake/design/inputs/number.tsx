// @flow
import React from 'react'

import { format } from 'intake/utils'

import { TextEl } from './text'

export const NumberInput = ({ value, onChange, ...props }: any) => {
  const amount = format.integer.toString(value)
  const _onChange = (e) => {
    const val = e.target.value
    const newAmount = format.integer.toValue(val)
    if (newAmount || val === '' || newAmount === 0) {
      onChange(newAmount)
    }
  }

  return (
    <TextEl
      type="text"
      inputMode="numeric"
      value={amount}
      onChange={_onChange}
      {...props}
    />
  )
}
