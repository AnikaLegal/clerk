import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'

import { actions } from 'state'
import InputField from 'components/generic/input-field'
import DropdownField from 'components/generic/dropdown-field'
import Button from 'components/generic/button'
import FadeIn from 'components/generic/fade-in'
import { FIELD_TYPES, FIELD_TYPES_DISPLAY } from 'consts'


// Key which we use to check whether the question has changed.
const getQuestionKey = q => [
  q.modifiedAt,
  q.parentTransitions.map(getTransitionKey).join('-')
].join('-')


// Key which we use to check whether a transition has changed
const getTransitionKey = t =>
  t.modifiedAt


// Form to update an existing question.
class UpdateQuestionForm extends Component {
  static propTypes = {
    script: PropTypes.shape({
      id: PropTypes.number.isRequired,
    }).isRequired,
    question: PropTypes.shape({
      id: PropTypes.number.isRequired,
      name: PropTypes.string.isRequired,
      prompt: PropTypes.string.isRequired,
      fieldType: PropTypes.string.isRequired,
      parentTransitions: PropTypes.array.isRequired,
    }).isRequired,
  }

  constructor(props) {
    super(props)
    this.state = {
      name: props.question.name,
      prompt: props.question.prompt,
      fieldType: props.question.fieldType,
    }
  }

  onInput = fieldName => e =>
    this.setState({ [fieldName]: e.target.value })

  render() {
    const { script, question } = this.props
    const { name, isFirst, prompt, fieldType } = this.state
    return (
      <FadeIn className="mb-2">
        <InputField
          label="Name"
          type="text"
          placeholder="Question name (internal use)"
          value={name}
          onChange={this.onInput('name')}
        />
        <InputField
          label="Prompt"
          type="text"
          placeholder="Prompt for the user to answer"
          value={prompt}
          onChange={this.onInput('prompt')}
        />
        <DropdownField
            label="Type"
            placeholder="Select question data type"
            value={fieldType}
            onChange={this.onInput('fieldType')}
            options={FIELD_TYPES.map(fieldType => [fieldType, FIELD_TYPES_DISPLAY[fieldType]])}
          />
      </FadeIn>
    )
  }
}

const mapStateToProps = state => ({
  scripts: state.data.script,
  questions: state.data.question,
})
const mapDispatchToProps = dispatch => ({
  // updateQuestion: question => dispatch(actions.question.update(question)),
  // removeQuestion: id => dispatch(actions.question.remove(id)),
})
export default connect(mapStateToProps, mapDispatchToProps)(UpdateQuestionForm)
export { getQuestionKey }
