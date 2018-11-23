import React, { Component } from 'react'
import { connect } from 'react-redux'

import QuestionForm from 'components/question-form'
import Button from 'components/generic/button'
import { actions } from 'state'

class FormBuilder extends Component {

  render() {
    const { script, createQuestion } = this.props
    return (
      <div>
        <Button
          className="mb-3"
          onClick={createQuestion}>
          Add New Question
        </Button>
        {Object.keys(script)
          .sort(sortQuestions(script))
          .map(k => (
            <QuestionForm key={k} question={script[k]} />
          )
        )}
      </div>
    )
  }
}

const sortQuestions = script => (a, b) => {
  if (script[a].start) return -1
  return 1
}


const mapStateToProps = state => ({
  script: state.script,
})
const mapDispatchToProps = dispatch => ({
  createQuestion: () => dispatch(actions.question.create()),
})
export default connect(mapStateToProps, mapDispatchToProps)(FormBuilder)
