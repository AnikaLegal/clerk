import React from 'react'
import PropTypes from 'prop-types'

import TextInput from './text'
import BooleanInput from './boolean'

const INPUT_LOOKUP = {
  TEXT: TextInput,
  NUMBER: TextInput,
  BOOLEAN: BooleanInput,
}

const Input = ({ fieldType, prompt, value, onChange, autoFocus }) => {
  const DataTypeInput = INPUT_LOOKUP[fieldType]
  return (
    <DataTypeInput
      prompt={prompt}
      value={value}
      onChange={onChange}
      autoFocus={autoFocus}
    />
  )
}
Input.propTypes = {
  fieldType: PropTypes.string.isRequired,
  prompt: PropTypes.string.isRequired,
  value: PropTypes.string.isRequired,
  onChange: PropTypes.func.isRequired,
  autoFocus: PropTypes.bool,
}
Input.defaultProps = {
  autoFocus: false,
}

export default Input
