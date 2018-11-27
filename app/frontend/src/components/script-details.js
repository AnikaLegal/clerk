import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'

import { actions } from 'state'
import FadeIn from 'components/generic/fade-in'
import FirstQuestionForm from 'components/forms/first-question'
import CreateQuestionForm from 'components/forms/create-question'
import UpdateQuestionForm, {
  getQuestionKey,
} from 'components/forms/update-question'

// Questionnaire script details page,
// where a user can view and update a questionnaire.
class ScriptDetails extends Component {
  render() {
    const { scripts, questions } = this.props
    // Get script ID from the URL
    const scriptId = Number(this.props.match.params.id) || null
    if (!scriptId) {
      return null
    } else if (scripts.loading) {
      return (
        <FadeIn duration="1">
          <p>Loading...</p>
        </FadeIn>
      )
    }
    const script = scripts.lookup[scriptId]
    return (
      <FadeIn duration="0.2">
        <h1 className="mb-3">{script.name}</h1>
        <div className="mb-3">
          <FirstQuestionForm script={script} key={script.firstQuestion} />
        </div>
        <div className="mb-3">
          <CreateQuestionForm script={script} />
        </div>
        {questions.list
          .filter(q => q.script === script.id)
          .map(q => (
            <UpdateQuestionForm
              script={script}
              question={q}
              key={getQuestionKey(q)}
            />
          ))}
      </FadeIn>
    )
  }
}

const mapStateToProps = state => ({
  scripts: state.data.script,
  questions: state.data.question,
})
const mapDispatchToProps = dispatch => ({})
export default withRouter(
  connect(
    mapStateToProps,
    mapDispatchToProps
  )(ScriptDetails)
)
