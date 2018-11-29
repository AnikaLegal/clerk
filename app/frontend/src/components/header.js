import React, { Component } from 'react'
import { connect } from 'react-redux'
import { Link, withRouter } from 'react-router-dom'

import routes from 'routes'
import { actions } from 'state'

const headerRoutes = routes.filter(r => r.header)

class Header extends Component {
  onSaveClick = e => this.props.saveScript(this.props.script)

  render() {
    const { script, location } = this.props
    return (
      <nav className="navbar navbar-expand navbar-light bg-light mb-3">
        <a className="navbar-brand" href="/">
          Clerk
        </a>
        <ul className="navbar-nav ml-auto">
          {headerRoutes.map(({ path, name }) => (
            <li
              key={path}
              className={`nav-item ${location.pathname === path && 'active'}`}
            >
              <Link className="nav-link" to={path}>
                {name}
              </Link>
            </li>
          ))}
        </ul>
      </nav>
    )
  }
}

const mapStateToProps = state => ({
  script: state.script,
})
const mapDispatchToProps = dispatch => ({})
export default withRouter(
  connect(
    mapStateToProps,
    mapDispatchToProps
  )(Header)
)
