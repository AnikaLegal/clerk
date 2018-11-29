import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'

import Button from 'components/generic/button'
import Loading from '../loading'
import Input from './inputs'

class ScriptTest extends Component {
  static propTypes = {
    script: PropTypes.shape({
      id: PropTypes.number.isRequired,
      firstQuestion: PropTypes.number.isRequired,
    }).isRequired,
  }

  // Ensure we set the currentStep when questions have finished loading.
  static getDerivedStateFromProps(props, state) {
    if (state.loading && !props.questions.loading) {
      return {
        loading: false,
        currentStep: ScriptTest.getFirstStep(props),
      }
    } else {
      return {}
    }
  }

  static getFirstStep(props) {
    const firstQuestionId = props.script.firstQuestion
    return props.questions.lookup[firstQuestionId]
  }

  constructor(props) {
    super(props)
    this.state = {
      answers: {},
      loading: props.questions.loading,
      currentStep: null,
    }
  }

  componentDidMount() {
    if (!this.props.questions.loading) {
      this.setState({ currentStep: ScriptTest.getFirstStep(this.props) })
    }
  }

  onRestart = () =>
    this.setState({
      answers: {},
      currentStep: ScriptTest.getFirstStep(this.props),
    })

  onChangeAnswer = id => e => {
    const { answers } = this.state
    this.setState({ answers: { ...answers, [id]: e.target.value } })
  }

  onNextClick = e => {
    const { currentStep, answers } = this.state
    const questionList = this.getQuestions()

    // Find all the transitions that follow this question
    const transitions = questionList
      .reduce((trans, q) => [...trans, ...q.parentTransitions], [])
      .filter(trans => trans.previous === currentStep.id)

    // Split all transitions into conditional and unconditional
    const conditionalTransitions = transitions.filter(t => t.condition)
    const unconditionalTransitions = transitions.filter(t => !t.condition)

    // Greedily pick the first matching conditional transition
    let nextQuestionId = this.getNextQuestion(conditionalTransitions)

    // If there is no matching condition transition, try the unconditional ones
    if (!nextQuestionId) {
      nextQuestionId = this.getNextQuestion(unconditionalTransitions)
    }

    // Update currentStep
    const nextQuestion = this.props.questions.lookup[nextQuestionId]
    this.setState({ currentStep: nextQuestion })
  }

  getNextQuestion = transitions => {
    for (let transition of transitions) {
      if (this.isConditionValid(transition)) {
        return transition.next
      }
    }
  }

  isConditionValid = transition => {
    // If there's no condition it's automatically valid
    if (!transition.condition) return true
    // Otherwise, we need to evaluate the condition
    const variable = this.state.answers[transition.variable]
    const value = transition.value
    return conditionLookup[transition.condition](variable, value)
  }

  getQuestions = () =>
    this.props.questions.list.filter(q => q.script === this.props.script.id)

  render() {
    const { answers, currentStep, loading } = this.state
    const { questions } = this.props
    const questionList = this.getQuestions()
    if (loading) return <Loading />
    if (questionList.length < 1) return <p>No questions to ask</p>
    if (!currentStep) {
      return (
        <div>
          <h1>Your answers</h1>
          {Object.keys(answers).map(id => (
            <p key={id}>
              <strong>{questions.lookup[id].name}:</strong>
              <span> {answers[id]}</span>
            </p>
          ))}
          <Button onClick={this.onRestart}>Start Again</Button>
        </div>
      )
    }
    return (
      <div>
        <Input
          prompt={currentStep.prompt}
          fieldType={currentStep.fieldType}
          value={answers[currentStep.id] || ''}
          onChange={this.onChangeAnswer(currentStep.id)}
          autoFocus
        />
        <div
          style={{
            width: '100%',
            maxWidth: '40rem',
            margin: '0 auto',
            padding: '0.375rem 0.75rem',
          }}
        >
          <Button
            onClick={this.onNextClick}
            disabled={!answers[currentStep.id]}
          >
            Next Step
          </Button>
        </div>
      </div>
    )
  }
}

const conditionLookup = {
  EQUALS: (variable, value) => variable === value,
}

const mapStateToProps = state => ({
  questions: state.data.question,
})
const mapDispatchToProps = dispatch => ({})
export default connect(
  mapStateToProps,
  mapDispatchToProps
)(ScriptTest)
