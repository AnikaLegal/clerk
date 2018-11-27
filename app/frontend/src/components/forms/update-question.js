import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'

import { actions } from 'state'
import debounce from 'utils/debounce'
import InputField from 'components/generic/input-field'
import DropdownField from 'components/generic/dropdown-field'
import Button from 'components/generic/button'
import { FIELD_TYPES, FIELD_TYPES_DISPLAY } from 'consts'

// Key which we use to check whether the question has changed.
const getQuestionKey = q =>
  [q.modifiedAt, q.parentTransitions.map(getTransitionKey).join('-')].join('-')

// Key which we use to check whether a transition has changed
const getTransitionKey = t => t.modifiedAt

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
      loading: false,
      name: props.question.name,
      prompt: props.question.prompt,
      fieldType: props.question.fieldType,
    }
  }

  debounce = debounce(1600)

  onSubmit = () => {
    const { question, updateQuestion } = this.props
    const { name, prompt, fieldType } = this.state
    this.setState({ loading: true })
    updateQuestion(question.id, name, prompt, fieldType)
  }

  onInput = fieldName => e => {
    this.setState({ [fieldName]: e.target.value }, () =>
      this.debounce(this.onSubmit)()
    )
  }

  render() {
    const { script, question } = this.props
    const { name, loading, prompt, fieldType } = this.state
    return (
      <div className="mb-2">
        <InputField
          label="Name"
          type="text"
          placeholder="Question name (internal use)"
          value={name}
          onChange={this.onInput('name')}
          readOnly={loading}
        />
        <InputField
          label="Prompt"
          type="text"
          placeholder="Prompt for the user to answer"
          value={prompt}
          onChange={this.onInput('prompt')}
          readOnly={loading}
        />
        <DropdownField
          label="Type"
          placeholder="Select question data type"
          value={fieldType}
          onChange={this.onInput('fieldType')}
          disabled={loading}
          options={FIELD_TYPES.map(fieldType => [
            fieldType,
            FIELD_TYPES_DISPLAY[fieldType],
          ])}
        />
      </div>
    )
  }
}

const mapStateToProps = state => ({
  scripts: state.data.script,
  questions: state.data.question,
})
const mapDispatchToProps = dispatch => ({
  updateQuestion: (...args) => dispatch(actions.question.update(...args)),
  // TODO - remove question form
})
export default connect(
  mapStateToProps,
  mapDispatchToProps
)(UpdateQuestionForm)
export { getQuestionKey }
