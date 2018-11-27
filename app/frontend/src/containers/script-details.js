import React, { Component } from 'react'
import { connect } from 'react-redux'

import { actions } from 'state'
import ErrorBoundary from 'components/generic/error-boundary'
import ErrorModal from 'components/modals/error'
import ScriptDetails from 'components/script-details'

class ScriptDetailsContainer extends Component {
  componentDidMount() {
    this.props.listScripts()
    this.props.listQuestions()
  }

  render() {
    const { errors, showError, clearError } = this.props
    return (
      <div>
        {showError && <ErrorModal onClose={clearError} errors={errors} />}
        <ErrorBoundary>
          <ScriptDetails />
        </ErrorBoundary>
      </div>
    )
  }
}

const mapStateToProps = state => ({
  showError: state.error.visible,
  errors: state.error.errors,
})
const mapDispatchToProps = dispatch => ({
  clearError: () => dispatch(actions.error.clear()),
  listScripts: () => dispatch(actions.script.list()),
  listQuestions: () => dispatch(actions.question.list()),
})
export default connect(
  mapStateToProps,
  mapDispatchToProps
)(ScriptDetailsContainer)
