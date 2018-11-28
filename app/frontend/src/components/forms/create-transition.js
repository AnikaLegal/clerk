import React, { Component } from 'react'
import { connect } from 'react-redux'
import PropTypes from 'prop-types'

import { actions } from 'state'
import Button from 'components/generic/button'
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
    this.setState({ loading: true }, () => (
      createTransition(question.id, previous, condition, variable, value).then(
        this.setState({ ...INITIAL_STATE })
      )
    ))
  }

  toggleOpen = () => this.setState({ isOpen: !this.state.isOpen })

  getOptions = () =>
    this.props.questions.list
      .filter(q => q.script === this.props.script.id)
      .filter(q => q.id !== this.props.question.id)
      .map(q => [q.id, q.name])

  isFormValid = () =>
    !this.state.loading &&
    this.state.previous && (
      (
        this.state.condition &&
        this.state.variable &&
        this.state.value
      ) || (
        !this.state.condition &&
        !this.state.variable &&
        !this.state.value
      )
    )

  render() {
    const { questions, question, script } = this.props
    const { previous, condition, variable, value, isOpen } = this.state
    if (!isOpen) {
      return <Button onClick={this.toggleOpen}>Add Parent</Button>
    }
    const options = this.getOptions()
    return (
      <FadeIn>
        <div className="mb-1">
         <div className="mb-2">
            <DropdownField
              label="Follows"
              placeholder="Select preceding question"
              value={previous}
              onChange={this.onInput('previous')}
              options={options}
            />
          </div>
         <div className="mb-2">
            <DropdownField
              label="answer"
              placeholder="Answer to check (optional)"
              value={variable}
              onChange={this.onInput('variable')}
              options={options}
              nullable
            />
          </div>
         <div className="mb-2">
            <DropdownField
              label="condition"
              placeholder="Condition type  (optional)"
              value={condition}
              onChange={this.onInput('variable')}
              options={['EQUALS']}
              nullable
            />
          </div>
          <div className="mb-2">
            <InputField
              label="value"
              type="text"
              placeholder="Value for condition"
              value={value}
              onChange={this.onInput('value')}
            />
          </div>
          <div className="mt-3">
            <Button
              className="mr-2"
              onClick={this.onConfirm}
              disabled={!this.isFormValid()}
            >
              Add Parent
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
  createTransition: (...args) =>
    dispatch(actions.transition.create(...args)),
})
export default connect(
  mapStateToProps,
  mapDispatchToProps
)(CreateTransitionForm)
