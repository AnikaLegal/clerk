import uniqid from 'uniqid'

import { api } from 'state'
import { checkForError, handleJSONResponse, handleError } from './utils'


export default {
  script: {
    list: () => dispatch => {
      dispatch({ type: 'SET_LOADING', key: 'script' });
      return api.script.list()
        .then(handleJSONResponse(dispatch))
        .then(data => dispatch({ type: 'RECEIVE_LIST', key: 'script', data }))
        .catch(handleError(dispatch));
    },
  },
  question: {
    list: () => dispatch => {
      dispatch({ type: 'SET_LOADING', key: 'question' });
      return api.question.list()
        .then(handleJSONResponse(dispatch))
        .then(data => dispatch({ type: 'RECEIVE_LIST', key: 'question', data }))
        .catch(handleError(dispatch));
    },
    // create: () => {
    //   return { type: 'CREATE_QUESTION', id: `${uniqid()}-${uniqid()}` }
    // },
    // update: (question) => ({ type: 'UPDATE_QUESTION', question }),
    // remove: id => ({ type: 'REMOVE_QUESTION', id }),
    // removeFollows: (id, follows) => ({ type: 'REMOVE_FOLLOWS', id, follows }),
    // addFollows: (id, prev, when, value) => ({ type: 'ADD_FOLLOWS', id, prev, when, value }),
  },
  // script: {
  //   upload: script => ({ type: 'UPLOAD_SCRIPT', script }),
  //   list: () => dispatch => {
  //     dispatch({ type: 'SET_LOADING', key: 'script' })
  //     return api.script.list()
  //       .then(r => r.json())
  //       .then(json => dispatch({
  //         type: 'RECEIVE_LIST',
  //         key: 'script',
  //         data: Object.values(json.data).map(el => ({...el, id: null}))
  //       }))
  //       .catch(console.error)
  //   },
    // save: script => dispatch => {
    //   const exported = exportScript(script)
    //   dispatch({ type: 'SET_LOADING', key: 'script' })
    //   return api.script.insert(exported)
    //     .then(() => dispatch({ type: 'UNSET_LOADING', key: 'script' }))
    //     .catch(console.error)
    // }
  // },
}
