import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'

import { actions } from 'state'
import FollowsField from 'components/follows-field'
import InputField from 'components/generic/input-field'
import CheckboxField from 'components/generic/checkbox-field'
import DropdownField from 'components/generic/dropdown-field'
import Button from 'components/generic/button'
import ErrorList from 'components/generic/error-list'
import { FIELD_KEYS, FIELD_TYPES } from 'consts'

import styles from 'styles/question-form.module.scss'

const FIELD_TYPES_DISPLAY = {
  text: 'Text',
  number: 'Number',
  boolean: 'Yes / No',
}

class QuestionForm extends Component {
  static propTypes = {

  }

  onInput = fieldName => e => {
    const question = { ...this.props.question, [fieldName]: e.target.value }
    this.props.updateQuestion(question)
  }

  onRemove = e => {
    this.props.removeQuestion(this.props.question.id)
  }

  render() {
    const { script, question } = this.props
    return (
      <div className={styles.questionForm}>
        <div className={styles.inputs}>
          <InputField
            label="Prompt"
            type="text"
            placeholder="Question prompt - eg. 'Have you contacted your landlord?'"
            value={question.prompt}
            onChange={this.onInput('prompt')}
          />
          <DropdownField
            label="Type"
            placeholder="Select question data type"
            value={question.type}
            onChange={this.onInput('type')}
            options={FIELD_TYPES.map(fieldType => [fieldType, FIELD_TYPES_DISPLAY[fieldType]])}
          />
          <FollowsField question={question} />
          <CheckboxField
            label="Starting question"
            value={question.start}
            disabled={Object.values(script).some(q => q.start)}
            onChange={this.onInput('start')}
          />
        </div>
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
  updateQuestion: question => dispatch(actions.question.update(question)),
  removeQuestion: id => dispatch(actions.question.remove(id)),
})
export default connect(
  mapStateToProps,
  mapDispatchToProps
)(QuestionForm)
