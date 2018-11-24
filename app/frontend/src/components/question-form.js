import React, { Component } from 'react'
import { connect } from 'react-redux'

import { actions } from 'state'
import FollowsField from 'components/follows-field'
import InputField from 'components/generic/input-field'
import CheckboxField from 'components/generic/checkbox-field'
import DropdownField from 'components/generic/dropdown-field'
import Button from 'components/generic/button'
import ErrorList from 'components/generic/error-list'
import { FIELD_KEYS, FIELD_TYPES, CONDITIONS, MANDATORY_FIELDS } from 'consts'

import styles from 'styles/question-form.module.scss'

const FIELD_TYPES_DISPLAY = {
  text: 'Text',
  email: 'Email',
  'multiple choice': 'Multiple Choice',
  'single choice': 'Single Choice',
  boolean: 'Yes / No',
  date: 'Date',
  info: 'Information',
  number: 'Number',
}

const getInitialState = question => ({
  errors: [],
  changed: false,
  // Question fields
  id: question.id,
  prompt: question.prompt || '',
  type: question.type || '',
  follows: question.follows || '',
  start: question.start || false,
})

class QuestionForm extends Component {
  constructor(props) {
    super(props)
    this.state = { ...getInitialState(props.question) }
  }

  onInput = fieldName => e => this.setState({ [fieldName]: e.target.value, changed: true })

  onSubmit = e => {
    const question = this.getQuestion()
    this.props.updateQuestion(question)
    this.setState({ errors: [], changed: false })
  }

  onFollowsChange = follows => {
    this.setState({ follows })
  }

  onRemove = e => {
    this.props.removeQuestion(this.props.question.id)
  }

  onReset = e => {
    this.setState({ ...getInitialState(this.props.question) })
  }

  getQuestion = () =>
    FIELD_KEYS.filter(k => this.state[k])
      .map(k => [k, this.state[k]])
      .reduce((obj, [k, v]) => ({ ...obj, [k]: v }), {})

  render() {
    const { id, start, prompt, type, then, errors, changed } = this.state
    const { script } = this.props
    return (
      <div className={`${styles.questionForm} ${changed && styles.changed}`}>
        <div className={styles.inputs}>
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
          <FollowsField 
            script={script}
            questionId={id}
            onChange={this.onFollowsChange}
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
          btnStyle="primary"
          onClick={this.onSubmit}
          className="mr-1"
          disabled={!MANDATORY_FIELDS.every(f => this.state[f])}
        >
          Update
        </Button>
        <Button btnStyle="light" onClick={this.onReset} className="mr-1">
          Reset
        </Button>
        <Button btnStyle="light" onClick={this.onRemove} className="mr-1">
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
  updateQuestion: (question) => dispatch(actions.question.update(question)),
  removeQuestion: id => dispatch(actions.question.remove(id)),
})
export default connect(
  mapStateToProps,
  mapDispatchToProps
)(QuestionForm)
