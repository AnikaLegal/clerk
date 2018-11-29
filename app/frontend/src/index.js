import ReactDOM from 'react-dom'
import React, { Component } from 'react'
import { BrowserRouter, Route, Switch } from 'react-router-dom'
import { Provider } from 'react-redux'

import { store } from 'state'
import routes from 'routes'
import Header from 'components/header'

import 'styles/main.global.scss'

class App extends Component {
  render() {
    return (
      <Provider store={store}>
        <BrowserRouter>
          <div>
            <Header />
            <div className="container">
              <div className="row">
                <div className="col">
                  <Switch>
                    {routes.map(({ path, exact, RouteComponent }) => (
                      <Route key={path} path={path} exact={exact}>
                        <RouteComponent />
                      </Route>
                    ))}
                  </Switch>
                </div>
              </div>
            </div>
          </div>
        </BrowserRouter>
      </Provider>
    )
  }
}

ReactDOM.render(<App />, document.getElementById('app'))
