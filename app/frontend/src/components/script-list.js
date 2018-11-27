import React, { Component } from 'react'
import { connect } from 'react-redux'
import { Link } from 'react-router-dom'

import { actions } from 'state'
import urls from 'urls'
import FadeIn from 'components/generic/fade-in'
import CreateScriptForm from 'components/forms/create-script'

// Page listing all questionnaire scripts.
class ScriptList extends Component {

  render() {
    const { scripts } = this.props
    if (scripts.loading) {
      return <FadeIn duration="1"><p>Loading...</p></FadeIn>
    }
    return (
      <FadeIn duration="0.2">
        <h1 className="mb-3">Questionnaires</h1>
        <ul className="list-group mb-2">
          {scripts.list.map(script => (
            <Link
              to={urls.client.script.details(script.id)}
              key={script.id}
              className="list-group-item list-group-item-action"
            >
              {script.name}
            </Link>
          ))}
        </ul>
        <CreateScriptForm />
      </FadeIn>
    )
  }
}

const mapStateToProps = state => ({
  scripts: state.data.script,
})
const mapDispatchToProps = dispatch => ({})
export default connect(
  mapStateToProps,
  mapDispatchToProps
)(ScriptList)
