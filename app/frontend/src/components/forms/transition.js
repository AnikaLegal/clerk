/*
Common transition form component, shared by create / update transition forms
*/
import React from 'react'

import { CONDITIONS, CONDITIONS_DISPLAY } from 'consts'
import InputField from 'components/generic/input-field'
import DropdownField from 'components/generic/dropdown-field'

const TransitionForm = ({
  isCreate,
  onInput,
  questionOptions,
  previous,
  condition,
  variable,
  value,
}) => (
  <div>
    <div className="mb-2">
      <DropdownField
        label="Follows"
        placeholder="Select preceding question"
        value={previous}
        onChange={onInput('previous')}
        options={questionOptions}
      />
    </div>
    <div className="mb-2">
      <DropdownField
        label="answer"
        placeholder="Answer to check (optional)"
        value={variable}
        onChange={onInput('variable')}
        options={questionOptions}
        nullable
      />
    </div>
    <div className="mb-2">
      <DropdownField
        label="condition"
        placeholder="Condition type  (optional)"
        value={condition}
        nullable
        onChange={onInput('condition')}
        options={CONDITIONS.map(condition => [
          condition,
          CONDITIONS_DISPLAY[condition],
        ])}
      />
    </div>
    <div className="mb-2">
      <InputField
        label="value"
        type="text"
        placeholder="Value for condition (optional)"
        value={value}
        onChange={onInput('value')}
      />
    </div>
  </div>
)

const isFormValid = ({ previous, condition, variable, value }) =>
  previous &&
  ((condition && variable && value) || (!condition && !variable && !value))

const getQuestionOptions = (questions, question, script) =>
  questions.list
    .filter(q => q.script === script.id)
    .filter(q => q.id !== question.id)
    .map(q => [q.id, q.name])

export default TransitionForm
export { isFormValid, getQuestionOptions }
