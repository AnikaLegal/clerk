import React, { Component } from 'react'
import { connect } from 'react-redux'
import PropTypes from 'prop-types'
import classNames from 'classnames/bind'

import { actions } from 'state'
import debounce from 'utils/debounce'
import { CONDITIONS, CONDITIONS_DISPLAY } from 'consts'
import Button from 'components/generic/button'
import TransitionForm, {
  isFormValid,
  getQuestionOptions,
} from 'components/forms/transition'
import styles from 'styles/update-form.module.scss'

const cx = classNames.bind(styles)

class UpdateTransitionForm extends Component {
  static propTypes = {
    script: PropTypes.shape({
      id: PropTypes.number.isRequired,
    }).isRequired,
    question: PropTypes.shape({
      id: PropTypes.number.isRequired,
    }).isRequired,
    transition: PropTypes.shape({
      id: PropTypes.number.isRequired,
      previous: PropTypes.number.isRequired,
      next: PropTypes.number.isRequired,
      condition: PropTypes.string,
      variable: PropTypes.number,
      value: PropTypes.string,
    }).isRequired,
  }

  constructor(props) {
    super(props)
    this.state = {
      loading: false,
      // Transition fields
      previous: props.transition.previous,
      condition: props.transition.condition || '',
      variable: props.transition.variable || '',
      value: props.transition.value || '',
    }
  }

  debounce = debounce(1600)

  onInput = fieldName => e => {
    this.setState({ [fieldName]: e.target.value }, () =>
      this.debounce(this.onSubmit)()
    )
  }

  onSubmit = () => {
    const { transition, question, updateTransition } = this.props
    const { previous, condition, variable, value } = this.state
    if (!isFormValid(this.state)) return
    this.setState({ loading: true }, () =>
      updateTransition({
        transitionId: transition.id,
        questionId: question.id,
        previous: previous,
        condition: condition,
        variable: variable,
        value: value,
      })
    )
  }

  onToggleOpen = () => this.props.toggleOpen(this.props.transition.id)

  hasChanged = () =>
    ['previous', 'condition', 'variable', 'value'].reduce((bool, field) => {
      const fieldHasChanged = this.props.transition[field] !== this.state[field]
      const isInitialSetting =
        this.props.transition[field] === null && this.state[field] === ''
      return bool || (fieldHasChanged && !isInitialSetting)
    }, false)

  render() {
    // TODO - check for valid before hitting API
    const {
      question,
      script,
      transition,
      questions,
      openTransitions,
    } = this.props
    const { previous, condition, variable, value } = this.state
    if (!openTransitions[transition.id]) {
      return (
        <div
          className={cx('list-group-item', 'closed', 'list-group-item-action', {
            changed: this.hasChanged(),
            invalid: !isFormValid(this.state),
          })}
          onClick={this.onToggleOpen}
        >
          Follows the question &ldquo;{questions.lookup[previous].name}&rdquo;{' '}
          {condition && (
            <span>
              if the answer to &ldquo;{questions.lookup[variable].name}&rdquo;{' '}
              {CONDITIONS_DISPLAY[condition]} &ldquo;{value}&rdquo;
            </span>
          )}
        </div>
      )
    }
    const options = getQuestionOptions(questions, question, script)
    return (
      <div
        className={cx('list-group-item', 'open', {
          changed: this.hasChanged(),
          invalid: !isFormValid(this.state),
        })}
      >
        <TransitionForm
          onInput={this.onInput}
          questionOptions={options}
          {...this.state}
        />
        <div className="mt-3">
          <Button btnStyle="secondary" onClick={this.onToggleOpen}>
            Hide
          </Button>
        </div>
      </div>
    )
  }
}

const mapStateToProps = state => ({
  openTransitions: state.selection.transition.open,
  questions: state.data.question,
})
const mapDispatchToProps = dispatch => ({
  updateTransition: (...args) => dispatch(actions.transition.update(...args)),
  toggleOpen: (...args) =>
    dispatch(actions.selection.transition.toggleOpen(...args)),
})
export default connect(
  mapStateToProps,
  mapDispatchToProps
)(UpdateTransitionForm)
