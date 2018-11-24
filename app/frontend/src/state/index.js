import { applyMiddleware, createStore } from 'redux'
import thunkMiddleware from 'redux-thunk'
import { createLogger } from 'redux-logger'

import api from './api'
import reducer from './reducer'
import actions from './actions'
import initialState from './init'

const loggerMiddleware = createLogger()
const middleware = applyMiddleware(thunkMiddleware, loggerMiddleware)
const store = createStore(reducer, initialState, middleware)

export { store, actions, api }
