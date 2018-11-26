import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'

import { FIELD_TYPES } from 'consts'
import { actions } from 'state'
import Button from 'components/generic/button'
import InputField from 'components/generic/input-field'
import DropdownField from 'components/generic/dropdown-field'
import CheckboxField from 'components/generic/checkbox-field'

const FIELD_TYPES_DISPLAY = {
  text: 'Text',
  number: 'Number',
  boolean: 'Yes / No',
}

const INITIAL_STATE = {
  loading: false, // Whether form is loading
  isOpen: false, // Whether the form is open / closed
  // Question fields
  name: '',
  isFirst: false,
  prompt: '',
  fieldType: '',
}

// Form to create a new questionnaire script.
class CreateQuestionForm extends Component {
  static propTypes = {
    script: PropTypes.shape({
      id: PropTypes.number.isRequired,
    }).isRequired
  }

  constructor(props) {
    super(props)
    this.state = { ...INITIAL_STATE }
  }

  onConfirm = () => {
    const { script, createQuestion } = this.props
    const { name } = this.state
    this.setState({ loading: true })
    createQuestion(script.id, name, isFirst, prompt, fieldType)
      .then(this.setState({ ...INITIAL_STATE }))
  }

  onInput = fieldName => e =>
    this.setState({ [fieldName]: e.target.value })

  toggleOpen = () =>
    this.setState({ isOpen: !this.state.isOpen })

  isFormValid = () =>
    !this.state.loading &&
    this.state.name &&
    this.state.prompt &&
    this.state.fieldType

  render() {
    const { name, isFirst, prompt, fieldType, isOpen } = this.state
    if (!isOpen) {
      return (
        <Button onClick={this.toggleOpen}>
          Add Question
        </Button>
      )
    }
    return (
      <div>
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
        <CheckboxField
          label="Is this the first question?"
          value={isFirst}
          onChange={this.onInput('isFirst')}
        />
        <div className="mt-2">
          <Button
            className="mr-2"
            onClick={this.onConfirm}
            disabled={!this.isFormValid()}
          >
            Add
          </Button>
          <Button
            onClick={this.toggleOpen}
            btnStyle="danger"
          >
            Close
          </Button>
        </div>
      </div>
    )
  }
}


const mapStateToProps = () => ({})
const mapDispatchToProps = dispatch => ({
  createQuestion: name => dispatch(actions.question.create(name)),
})
export default connect(mapStateToProps, mapDispatchToProps)(CreateQuestionForm)
