import React, { Component } from 'react'
import { connect } from 'react-redux'

import InputField from 'components/generic/input-field'
import CheckboxField from 'components/generic/checkbox-field'
import DropdownField from 'components/generic/dropdown-field'
import Button from 'components/generic/button'

const Question = ({ value, label, prompt, onChange, readOnly, onNext }) => (
  <div className="mb-4">
    <p>{prompt}</p>
    <InputField label={label} type="text" value={value} onChange={onChange} readOnly={readOnly} />
    {!readOnly && (
      <Button className="mt-2" onClick={onNext} disabled={!value}>
        Next Question
      </Button>
    )}
  </div>
)

class Questionnaire extends Component {
  constructor(props) {
    super(props)
    this.state = {
      data: {},
      currentStep: null,
      currentAnswer: '',
      answeredSteps: [],
    }
  }

  componentDidMount() {
    const startQuestion = Object.values(this.props.script).find(q => q.start)
    if (startQuestion) this.setState({ currentStep: startQuestion.name })
  }

  onNextClick = () => {
    const { currentStep, currentAnswer, answeredSteps, data } = this.state
    const { script } = this.props
    if (currentAnswer) {
      this.setState({
        currentStep: script[currentStep].then,
        data: { ...data, [currentStep]: currentAnswer },
        answeredSteps: [...answeredSteps, currentStep],
        currentAnswer: '',
      })
    }
  }

  onAnswerChange = e => this.setState({ currentAnswer: e.target.value })

  hasQuestions = () => Object.keys(this.props.script).length > 0

  render() {
    const { data, currentStep, answeredSteps, currentAnswer } = this.state
    const { script } = this.props
    if (!this.hasQuestions()) {
      return <p>No questions to test</p>
    }
    return (
      <div>
        {answeredSteps.map(stepName => (
          <Question
            label={stepName}
            key={stepName}
            prompt={script[stepName].prompt}
            value={data[stepName]}
            readOnly={true}
          />
        ))}
        {currentStep && (
          <Question
            label={currentStep}
            prompt={script[currentStep].prompt}
            value={currentAnswer}
            onChange={this.onAnswerChange}
            onNext={this.onNextClick}
          />
        )}
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
