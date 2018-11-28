import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import classNames from 'classnames/bind'

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
    } else if (scripts.list.length < 1) {
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
        <div className="list-group mb-3">
          <div className="list-group-item">
            <FirstQuestionForm script={script} key={script.firstQuestion} />
          </div>
          {questions.list
            .filter(q => q.script === script.id)
            .map(q => (
              <div key={q.id} className="list-group-item">
                <UpdateQuestionForm
                  script={script}
                  question={q}
                  key={getQuestionKey(q)}
                />
              </div>
            ))}
        </div>
        <CreateQuestionForm script={script} />
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
