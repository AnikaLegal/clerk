import ReactDOM from 'react-dom'
import React, { Component } from 'react'
import { BrowserRouter, Route, Switch } from 'react-router-dom'
import { Provider } from 'react-redux'

import { store } from 'state'
import FormBuilder from 'components/form-builder'
import FormGraph from 'components/form-graph'
import Header from 'components/header'
import Questionnaire from 'components/questionnaire'

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
                    <Route path="/test">
                      <Questionnaire />
                    </Route>
                    <Route path="/graph">
                      <FormGraph />
                    </Route>
                    <Route path="/">
                      <FormBuilder />
                    </Route>
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

ReactDOM.render(<App/>, document.getElementById('app'))
