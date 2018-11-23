import React, { Component } from 'react'
import { connect } from 'react-redux'

import { actions } from 'state'
import ScriptValidator from 'validator'
import InputField from 'components/generic/input-field'
import CheckboxField from 'components/generic/checkbox-field'
import DropdownField from 'components/generic/dropdown-field'
import Button from 'components/generic/button'
import ErrorList from 'components/generic/error-list'
import {
  FIELD_KEYS,
  FIELD_TYPES,
  CONDITIONS,
  MANDATORY_FIELDS,
} from 'consts'

import styles from 'styles/question-form.module.scss'


const FIELD_TYPES_DISPLAY = {
  'text': 'Text',
  'email': 'Email',
  'multiple choice': 'Multiple Choice',
  'single choice': 'Single Choice',
  'boolean': 'Yes / No',
  'date': 'Date',
  'info': 'Information',
  'number': 'Number',
}

const getInitialState = (question) => ({
  errors: [],
  changed: false,
  // Question fields
  name: question.name || '',
  prompt: question.prompt || '',
  type: question.type || '',
  then: question.then || '',
  start: question.start || false,
})

class QuestionForm extends Component {
  constructor(props) {
    super(props);
    this.state = {...getInitialState(props.question)}
  }

  onInput = fieldName => e =>
    this.setState({ [fieldName]: e.target.value, changed: true })

  onSubmit = e => {
    const question = this.getQuestion()
    const validator = new ScriptValidator(this.props.script)
    const isValid = validator.canAddQuestion(question)
    if (isValid) {
      this.props.updateQuestion(this.props.question.name, question)
      this.setState({ errors: validator.errors, changed: false })
    } else {
      this.setState({ errors: validator.errors })
    }
  }

  onRemove = e => {
    this.props.removeQuestion(this.props.question.name)
  }

  onReset = e => {
    this.setState({...getInitialState(this.props.question)})
  }

  getQuestion = () =>
    FIELD_KEYS
      .filter(k => this.state[k])
      .map(k => [k, this.state[k]])
      .reduce((obj, [k, v]) => ({...obj, [k]: v}), {})

  render() {
    const { name, start, prompt, type, then, validator, errors, changed } = this.state
    const { script } = this.props
    return (
      <div className={`${styles.questionForm} ${changed && styles.changed}`}>
        <div className={styles.twoColumns}>
          <InputField
            label="Name"
            type="text"
            placeholder="A description of the question eg. 'Has contacted landlord'"
            value={name}
            onChange={this.onInput('name')}
          />
          <InputField
            label="Prompt"
            type="text"
            placeholder="Question prompt - eg. 'Have you contacted your landlord?'"
            value={prompt}
            onChange={this.onInput('prompt')}
          />
          <DropdownField
            label="Type"
            placeholder="Select question data type"
            value={type}
            onChange={this.onInput('type')}
            options={FIELD_TYPES.map(fieldType => [fieldType, FIELD_TYPES_DISPLAY[fieldType]])}
          />
          <DropdownField
            label="Then"
            placeholder="Select the next question"
            value={then}
            onChange={this.onInput('then')}
            options={Object.keys(script)
              .filter(k => k !== name && k !== this.props.question.name)
              .map(k => [k, k])}
          />
          <CheckboxField
            label="Starting question"
            value={start}
            disabled={Object.values(script).some(q => q.start)}
            onChange={this.onInput('start')}
          />
        </div>
        <ErrorList errors={errors} />
        <Button
          btnStyle="light"
          onClick={this.onSubmit}
          className="mr-1"
          disabled={!MANDATORY_FIELDS.every(f => this.state[f])}
        >
          Update
        </Button>
        <Button
          btnStyle="light"
          onClick={this.onReset}
          className="mr-1"
        >
          Reset
        </Button>
        <Button
          btnStyle="light"
          onClick={this.onRemove}
          className="mr-1"
        >
          Remove
        </Button>
      </div>
    )
  }
}


const mapStateToProps = state => ({
  script: state.script,
})
const mapDispatchToProps = dispatch => ({
    updateQuestion: (prevName, question) => dispatch(actions.question.update(prevName, question)),
    removeQuestion: name => dispatch(actions.question.remove(name)),
})
export default connect(mapStateToProps, mapDispatchToProps)(QuestionForm)
