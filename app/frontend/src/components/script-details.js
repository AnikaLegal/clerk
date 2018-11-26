import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'

import { actions } from 'state'

class ScriptDetails extends Component {
  componentDidMount() {
    this.props.listScripts()
    this.props.listQuestions()
  }

  render() {
    const { scripts, questions } = this.props
    const scriptId = Number(this.props.match.params.id) || null
    if (!scriptId) {
      return null
    } else if (scripts.loading || questions.loading) {
      return <p>Loading...</p>
    }
    const script = scripts.lookup[scriptId]
    return <div>{script.id}</div>
  }
}

const mapStateToProps = state => ({
  scripts: state.data.script,
  questions: state.data.question,
})
const mapDispatchToProps = dispatch => ({
  listScripts: () => dispatch(actions.script.list()),
  listQuestions: () => dispatch(actions.question.list()),
})
export default withRouter(
  connect(
    mapStateToProps,
    mapDispatchToProps
  )(ScriptDetails)
)
