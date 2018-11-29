import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter, Route, Switch } from 'react-router-dom'

import { actions } from 'state'
import ErrorBoundary from 'components/generic/error-boundary'
import ErrorModal from 'components/modals/error'
import ScriptDetails from 'components/script/details'
import ScriptHeader from 'components/script/header'
import Loading from 'components/script/loading'
import routes from 'components/script/routes'

class ScriptDetailsContainer extends Component {
  componentDidMount() {
    this.props.listScripts()
    this.props.listQuestions()
  }

  // Get script ID from the React Router URL match
  getScriptId = () => Number(this.props.match.params.id) || null

  render() {
    const { errors, showError, clearError, scripts } = this.props
    const scriptId = this.getScriptId()
    if (!scriptId) return null
    if (scripts.list.length < 1) return <Loading />
    const script = scripts.lookup[scriptId]
    return (
      <div>
        {showError && <ErrorModal onClose={clearError} errors={errors} />}
        <ScriptHeader script={script} />
        <Switch>
          {routes.map(({ path, RouteComponent }) => (
            <Route key={path} path={path} exact>
              <ErrorBoundary>
                <RouteComponent script={script} />
              </ErrorBoundary>
            </Route>
          ))}
        </Switch>
      </div>
    )
  }
}

const mapStateToProps = state => ({
  scripts: state.data.script,
  showError: state.error.visible,
  errors: state.error.errors,
})
const mapDispatchToProps = dispatch => ({
  clearError: () => dispatch(actions.error.clear()),
  listScripts: () => dispatch(actions.script.list()),
  listQuestions: () => dispatch(actions.question.list()),
})
export default withRouter(
  connect(
    mapStateToProps,
    mapDispatchToProps
  )(ScriptDetailsContainer)
)
