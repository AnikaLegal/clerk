import React, { Component } from 'react'
import { connect } from 'react-redux'
import { Link } from 'react-router-dom'

import { actions } from 'state'
import urls from 'urls'
import CreateScriptForm from 'components/forms/create-script'

class ScriptList extends Component {

  render() {
    const { scripts } = this.props
    return (
      <div>
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
      </div>
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
