import React, { Component } from 'react'
import { connect } from 'react-redux'
import PropTypes from 'prop-types'

import { actions } from 'state'
import { CONDITIONS, CONDITIONS_DISPLAY } from 'consts'
import Button from 'components/generic/button'
import TransitionForm, {
  isFormValid,
  getQuestionOptions,
} from 'components/forms/transition'
import DropdownField from 'components/generic/dropdown-field'
import InputField from 'components/generic/input-field'
import FadeIn from 'components/generic/fade-in'

const INITIAL_STATE = {
  loading: false, // Whether form is loading
  isOpen: false, // Whether the form is open / closed
  // Transition fields
  previous: '',
  condition: '',
  variable: '',
  value: '',
}

class CreateTransitionForm extends Component {
  static propTypes = {
    script: PropTypes.shape({
      id: PropTypes.number.isRequired,
    }).isRequired,
    question: PropTypes.shape({
      id: PropTypes.number.isRequired,
    }).isRequired,
  }

  constructor(props) {
    super(props)
    this.state = { ...INITIAL_STATE }
  }

  onInput = fieldName => e => this.setState({ [fieldName]: e.target.value })

  onConfirm = () => {
    const { createTransition, question } = this.props
    const { previous, condition, variable, value } = this.state
    this.setState({ loading: true }, () =>
      createTransition({
        questionId: question.id,
        previous: previous,
        condition: condition,
        variable: variable,
        value: value,
      }).then(this.setState({ ...INITIAL_STATE }))
    )
  }

  toggleOpen = () => this.setState({ isOpen: !this.state.isOpen })

  render() {
    const { questions, question, script } = this.props
    const { loading, previous, condition, variable, value, isOpen } = this.state
    if (!isOpen) {
      return (
        <Button btnStyle="light" onClick={this.toggleOpen}>
          Follow a Question
        </Button>
      )
    }
    const options = getQuestionOptions(questions, question, script)
    return (
      <FadeIn>
        <div className="mb-1">
          <TransitionForm
            isCreate
            onInput={this.onInput}
            questionOptions={options}
            {...this.state}
          />
          <div className="mt-3">
            <Button
              className="mr-2"
              onClick={this.onConfirm}
              disabled={loading || !isFormValid(this.state)}
            >
              Follow a Question
            </Button>
            <Button onClick={this.toggleOpen} btnStyle="danger">
              Close
            </Button>
          </div>
        </div>
      </FadeIn>
    )
  }
}

const mapStateToProps = state => ({
  questions: state.data.question,
})
const mapDispatchToProps = dispatch => ({
  createTransition: (...args) => dispatch(actions.transition.create(...args)),
})
export default connect(
  mapStateToProps,
  mapDispatchToProps
)(CreateTransitionForm)
