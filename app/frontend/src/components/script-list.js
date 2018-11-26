import React, { Component } from 'react'
import { connect } from 'react-redux'
import { Link } from 'react-router-dom'

import { actions } from 'state'
import urls from 'urls'

class ScriptList extends Component {
  componentDidMount() {
    this.props.listScripts()
  }

  render() {
    const { scripts } = this.props
    return (
      <div>
        {scripts.list.map(script => (
          <Link to={urls.client.script.details(script.id)} key={script.id}>
            <ul className="list-group mb-3">
              {script.id} - {script.name}
            </ul>
          </Link>
        ))}
      </div>
    )
  }
}

const mapStateToProps = state => ({
  scripts: state.data.script,
})
const mapDispatchToProps = dispatch => ({
  listScripts: () => dispatch(actions.script.list()),
})
export default connect(
  mapStateToProps,
  mapDispatchToProps
)(ScriptList)
