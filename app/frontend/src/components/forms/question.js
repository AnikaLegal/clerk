/*
Common question form component, shared by create / update question forms
*/
import React from 'react'

import { FIELD_TYPES, FIELD_TYPES_DISPLAY } from 'consts'
import InputField from 'components/generic/input-field'
import DropdownField from 'components/generic/dropdown-field'
import classNames from 'classnames/bind'

const QuestionForm = ({
  isCreate,
  onInput,
  name,
  prompt,
  fieldType,
  loading,
}) => (
  <div>
    <div className="mb-3">
      <InputField
        label="Name"
        type="text"
        placeholder="Question name"
        value={name}
        onChange={onInput('name')}
        autoFocus={isCreate}
        disabled={loading}
      />
    </div>
    <div className="mb-3">
      <InputField
        label="Prompt"
        type="text"
        placeholder="Prompt for the user to answer"
        value={prompt}
        onChange={onInput('prompt')}
        disabled={loading}
      />
    </div>
    <div className={classNames({ 'mb-4': !isCreate, 'mb-2': isCreate })}>
      <DropdownField
        label="Type"
        placeholder="Select question data type"
        value={fieldType}
        onChange={onInput('fieldType')}
        disabled={loading}
        options={FIELD_TYPES.map(fieldType => [
          fieldType,
          FIELD_TYPES_DISPLAY[fieldType],
        ])}
      />
    </div>
  </div>
)

const isFormValid = ({ name, prompt, fieldType }) => name && prompt && fieldType

export default QuestionForm
export { isFormValid }
