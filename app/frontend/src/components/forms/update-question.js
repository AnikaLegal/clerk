import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import classNames from 'classnames/bind'

import { actions } from 'state'
import debounce from 'utils/debounce'
import SubField from 'components/generic/sub-field'
import QuestionForm, { isFormValid } from 'components/forms/question'
import Button from 'components/generic/button'
import ErrorBoundary from 'components/generic/error-boundary'
import ConfirmationModal from 'components/modals/confirm'
import CreateTransitionForm from 'components/forms/create-transition'
import UpdateTransitionForm from 'components/forms/update-transition'
import { FIELD_TYPES, FIELD_TYPES_DISPLAY } from 'consts'
import styles from 'styles/update-form.module.scss'

const cx = classNames.bind(styles)

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
      parentTransitions: PropTypes.arrayOf(
        PropTypes.shape({
          id: PropTypes.number.isRequired,
          modifiedAt: PropTypes.string.isRequired,
        })
      ).isRequired,
    }),
  }

  constructor(props) {
    super(props)
    this.state = {
      loading: false,
      isDeleteOpen: false,
      name: props.question.name,
      prompt: props.question.prompt,
      fieldType: props.question.fieldType,
    }
  }

  debounce = debounce(1600)

  onSubmit = () => {
    const { question, updateQuestion } = this.props
    const { name, prompt, fieldType } = this.state
    if (!isFormValid(this.state)) return
    this.setState({ loading: true }, () =>
      updateQuestion({
        questionId: question.id,
        name: name,
        prompt: prompt,
        fieldType: fieldType,
      })
    )
  }

  onInput = fieldName => e => {
    this.setState({ [fieldName]: e.target.value }, () =>
      this.debounce(this.onSubmit)()
    )
  }

  onDelete = () =>
    this.props.deleteQuestion({ questionId: this.props.question.id })

  onToggleOpen = () => this.props.toggleOpen(this.props.question.id)

  onToggleDeleteOpen = () =>
    this.setState({ isDeleteOpen: !this.state.isDeleteOpen })

  hasChanged = () =>
    ['name', 'prompt', 'fieldType'].reduce(
      (bool, field) => bool || this.props.question[field] !== this.state[field],
      false
    )

  render() {
    const { script, question, openQuestions } = this.props
    const { name, isDeleteOpen } = this.state
    if (!openQuestions[question.id]) {
      return (
        <div
          className={cx('list-group-item', 'closed', 'list-group-item-action', {
            changed: this.hasChanged(),
            invalid: !isFormValid(this.state),
          })}
          onClick={this.onToggleOpen}
        >
          <SubField label="name">
            <div className={cx('closedLabel')}>{name}</div>
          </SubField>
        </div>
      )
    }
    return (
      <div
        className={cx('list-group-item', 'open', {
          changed: this.hasChanged(),
          invalid: !isFormValid(this.state),
        })}
      >
        <QuestionForm onInput={this.onInput} {...this.state} />
        <SubField label="follows" className="mb-3">
          <ErrorBoundary>
            <div className="list-group mb-2">
              {question.parentTransitions.length > 0 &&
                question.parentTransitions
                  .sort((a, b) => (a.id > b.id ? 1 : -1))
                  .map(t => (
                    <div key={t.id}>
                      <UpdateTransitionForm
                        key={t.modifiedAt}
                        question={question}
                        script={script}
                        transition={t}
                      />
                    </div>
                  ))}
              {question.parentTransitions.length < 1 && (
                <div className="list-group-item">
                  This question does not follow any other questions.
                </div>
              )}
            </div>
            <CreateTransitionForm script={script} question={question} />
          </ErrorBoundary>
        </SubField>
        <div className="mt-3 d-flex justify-content-between">
          <Button btnStyle="secondary" onClick={this.onToggleOpen}>
            Hide
          </Button>
          <Button onClick={this.onToggleDeleteOpen} btnStyle="danger">
            Delete
          </Button>
        </div>
        <ConfirmationModal
          isVisible={isDeleteOpen}
          onConfirm={this.onDelete}
          onCancel={this.onToggleDeleteOpen}
        >
          <p>
            <strong>Delete the question &ldquo;{name}&rdquo;?</strong>
          </p>
        </ConfirmationModal>
      </div>
    )
  }
}

const mapStateToProps = state => ({
  openQuestions: state.selection.question.open,
})
const mapDispatchToProps = dispatch => ({
  updateQuestion: (...args) => dispatch(actions.question.update(...args)),
  deleteQuestion: (...args) => dispatch(actions.question.delete(...args)),
  toggleOpen: (...args) =>
    dispatch(actions.selection.question.toggleOpen(...args)),
})
export default connect(
  mapStateToProps,
  mapDispatchToProps
)(UpdateQuestionForm)
export { getQuestionKey }
