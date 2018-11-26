import React, { Component } from 'react'
import { connect } from 'react-redux'

import InputField from 'components/generic/input-field'
import CheckboxField from 'components/generic/checkbox-field'
import DropdownField from 'components/generic/dropdown-field'
import Button from 'components/generic/button'

const FINISHED = 'FINISHED'

class Questionnaire extends Component {
  constructor(props) {
    super(props)
    this.state = {
      answers: {},
      currentStepId: null,
    }
  }

  componentDidMount() {
    const startId = this.findStartId()
    if (startId) this.setState({ currentStepId: startId })
  }

  onChangeAnswer = id => e => {
    const answers = this.state.answers
    console.warn(answers)
    this.setState({ answers: { ...answers, [id]: e.target.value } })
  }

  onNextClick = e => {
    const { currentStepId, answers } = this.state
    const { script } = this.props
    // Find next step
    let nextQuestionId = null
    for (let question of Object.values(script)) {
      for (let follow of question.follows) {
        const isIdMatch = follow.id === currentStepId
        const isWhenMatch = follow.when ? answers[follow.when.id] === follow.when.value : true

        if (isIdMatch && isWhenMatch) {
          nextQuestionId = question.id
          break
        }
      }
      if (nextQuestionId) break
    }
    // Update currentStepId
    this.setState({ currentStepId: nextQuestionId })
  }

  findStartId = () => {
    for (let i of Object.values(this.props.script)) {
      if (i.start) {
        return i.id
      }
    }
  }

  render() {
    const { answers, currentStepId } = this.state
    const { script } = this.props
    if (Object.keys(script).length < 1) return <p>No questions to ask</p>
    if (!currentStepId)
      return (
        <div>
          <h1>Your answers</h1>
          {Object.keys(answers).map(id => (
            <p key={id}>
              <strong>{script[id].prompt}:</strong> {answers[id]}
            </p>
          ))}
        </div>
      )
    const currentStep = script[currentStepId]
    return (
      <div>
        <InputField
          label={currentStep.prompt}
          type="text"
          value={answers[currentStepId] || ''}
          onChange={this.onChangeAnswer(currentStepId)}
          readOnly={false}
        />
        {<Button onClick={this.onNextClick}>Next Step</Button>}
      </div>
    )
  }
}

const mapStateToProps = state => ({
  script: state.script,
})
const mapDispatchToProps = dispatch => ({})
export default connect(
  mapStateToProps,
  mapDispatchToProps
)(Questionnaire)
