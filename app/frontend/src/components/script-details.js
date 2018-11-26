import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'

import { actions } from 'state'
import CreateQuestionForm from 'components/forms/create-question'

class ScriptDetails extends Component {

  render() {
    const { scripts, questions } = this.props
    const scriptId = Number(this.props.match.params.id) || null
    if (!scriptId) {
      return null
    } else if (scripts.loading || questions.loading) {
      return <p>Loading...</p>
    }
    const script = scripts.lookup[scriptId]
    return (
      <div>
        <h1 className="mb-3">{script.name}</h1>
        <CreateQuestionForm script={script} />
        {script.questions.map(id => (
          <div key={id} className="mb-2">
            {questions.lookup[id].name}
            <small>{questions.lookup[id].prompt}</small>
          </div>
        ))}
      </div>
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
