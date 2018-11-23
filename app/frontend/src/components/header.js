import React, { Component } from 'react'
import { connect } from 'react-redux'
import { Link, Route, withRouter, Switch } from 'react-router-dom'

import { actions } from 'state'

const routes = [
  {name: 'Build', path: '/',},
  {name: 'View', path: '/graph'},
  {name: 'Test', path: '/test'},
]

class Header extends Component {

  onUploadClick = e => this.input.click()
  onUploadChange = e => {
    const files = e.target.files
    if (files.length > 0) {
      const reader = new FileReader()
      const file = files[0]
      reader.onload = e => {
        const script = JSON.parse(e.target.result)
        this.props.uploadScript(script)
      }
      reader.readAsText(file);
    }
  }

  render() {
    const { script, location } = this.props
    return (
      <nav className="navbar navbar-expand navbar-light bg-light mb-3">
        <a className="navbar-brand" href="#">
          Clerk
          <Switch>
            {routes.map(route => (
              <Route key={route.path} path={route.path} exact>
                <span> - {route.name}</span>
              </Route>
            ))}
          </Switch>
        </a>
        <ul className="navbar-nav ml-auto">
          {routes.map(route => (
            <li key={route.path} className={`nav-item ${location.pathname === route.path && 'active'}`}>
              <Link className="nav-link" to={route.path}>{route.name}</Link>
            </li>
          ))}
          <li className="nav-item" onClick={this.onUploadClick}>
            <a href="#" className="nav-link">
              Upload
            </a>
            <input
              type="file"
              style={{display: 'none'}}
              onChange={this.onUploadChange}
              ref={r => { this.input = r; }}
            />
          </li>
          <li className="nav-item">
            <DownloadLink script={script}>
              Download
            </DownloadLink>
          </li>
        </ul>
      </nav>
    )
  }
}


const DownloadLink = ({ script, children }) => {
  const json = JSON.stringify(script, null, 2)
  const data = "text/json;charset=utf-8," + encodeURIComponent(json);
    return (
      <a href={`data:${data}`} download="script.json" className="nav-link">
        {children}
      </a>
    )
  }


const mapStateToProps = state => ({
  script: state.script,
})
const mapDispatchToProps = dispatch => ({
  uploadScript: (script) => dispatch(actions.script.upload(script)),
})
export default withRouter(connect(mapStateToProps, mapDispatchToProps)(Header))
