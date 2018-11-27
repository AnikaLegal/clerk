import uniqid from 'uniqid'

import { api } from 'state'
import { checkForError, handleJSONResponse, handleError } from './utils'

export default {
  // Actions affecting error messages
  error: {
    clear: () => ({ type: 'CLEAR_ERROR' }),
  },
  // Actions affecting questionnaire scripts
  script: {
    list: () => dispatch => {
      dispatch({ type: 'SET_LOADING', key: 'script' })
      return api.script
        .list()
        .then(handleJSONResponse(dispatch))
        .then(data => dispatch({ type: 'RECEIVE_LIST', key: 'script', data }))
        .catch(handleError(dispatch))
    },
    create: (...args) => dispatch => {
      dispatch({ type: 'SET_LOADING', key: 'script' })
      return api.script
        .create(...args)
        .then(handleJSONResponse(dispatch))
        .then(item => dispatch({ type: 'UPSERT_ITEM', key: 'script', item }))
        .catch(handleError(dispatch))
    },
    setFirstQuestion: (...args) => dispatch => {
      dispatch({ type: 'SET_LOADING', key: 'script' })
      return api.script
        .setFirstQuestion(...args)
        .then(handleJSONResponse(dispatch))
        .then(item => dispatch({ type: 'UPSERT_ITEM', key: 'script', item }))
        .catch(handleError(dispatch))
    },
  },
  // Actions affecting questions
  question: {
    list: () => dispatch => {
      dispatch({ type: 'SET_LOADING', key: 'question' })
      return api.question
        .list()
        .then(handleJSONResponse(dispatch))
        .then(data => dispatch({ type: 'RECEIVE_LIST', key: 'question', data }))
        .catch(handleError(dispatch))
    },
    create: (...args) => dispatch => {
      dispatch({ type: 'SET_LOADING', key: 'question' })
      return api.question
        .create(...args)
        .then(handleJSONResponse(dispatch))
        .then(item => dispatch({ type: 'UPSERT_ITEM', key: 'question', item }))
        .catch(handleError(dispatch))
    },
    // update: (question) => ({ type: 'UPDATE_QUESTION', question }),
    // remove: id => ({ type: 'REMOVE_QUESTION', id }),
    // removeFollows: (id, follows) => ({ type: 'REMOVE_FOLLOWS', id, follows }),
    // addFollows: (id, prev, when, value) => ({ type: 'ADD_FOLLOWS', id, prev, when, value }),
  },
}
