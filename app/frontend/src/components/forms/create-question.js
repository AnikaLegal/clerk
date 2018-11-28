import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'

import { FIELD_TYPES, FIELD_TYPES_DISPLAY } from 'consts'
import { actions } from 'state'
import QuestionForm, { isFormValid } from 'components/forms/question'
import Button from 'components/generic/button'
import FadeIn from 'components/generic/fade-in'

const INITIAL_STATE = {
  loading: false, // Whether form is loading
  isOpen: false, // Whether the form is open / closed
  // Question fields
  name: '',
  prompt: '',
  fieldType: '',
}

// Form to create a new questionnaire script.
class CreateQuestionForm extends Component {
  static propTypes = {
    script: PropTypes.shape({
      id: PropTypes.number.isRequired,
    }).isRequired,
  }

  constructor(props) {
    super(props)
    this.state = { ...INITIAL_STATE }
  }

  onConfirm = () => {
    const { script, createQuestion } = this.props
    const { name, prompt, fieldType } = this.state
    this.setState({ loading: true }, () =>
      createQuestion({
        scriptId: script.id,
        name: name,
        prompt: prompt,
        fieldType: fieldType,
      }).then(() => this.setState({ ...INITIAL_STATE }))
    )
  }

  onInput = fieldName => e => this.setState({ [fieldName]: e.target.value })

  onToggleOpen = () => this.setState({ isOpen: !this.state.isOpen })

  render() {
    const { loading, isOpen } = this.state
    if (!isOpen) {
      return <Button onClick={this.onToggleOpen}>Add Question</Button>
    }
    return (
      <FadeIn>
        <QuestionForm isCreate onInput={this.onInput} {...this.state} />
        <div className="mt-3">
          <Button
            className="mr-2"
            onClick={this.onConfirm}
            disabled={loading || !isFormValid(this.state)}
          >
            Add Question
          </Button>
          <Button onClick={this.onToggleOpen} btnStyle="danger">
            Close
          </Button>
        </div>
      </FadeIn>
    )
  }
}

const mapStateToProps = () => ({})
const mapDispatchToProps = dispatch => ({
  createQuestion: (...args) => dispatch(actions.question.create(...args)),
})
export default connect(
  mapStateToProps,
  mapDispatchToProps
)(CreateQuestionForm)
