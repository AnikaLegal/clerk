import uniqid from 'uniqid'

import { api } from 'state'
import { importScript, exportScript } from 'state/transform'


export default {
  question: {
    create: () => {
      return { type: 'CREATE_QUESTION', id: `${uniqid()}-${uniqid()}` }
    },
    update: (question) => ({ type: 'UPDATE_QUESTION', question }),
    remove: id => ({ type: 'REMOVE_QUESTION', id }),
    removeFollows: (id, follows) => ({ type: 'REMOVE_FOLLOWS', id, follows }),
    addFollows: (id, prev, when, value) => ({ type: 'ADD_FOLLOWS', id, prev, when, value }),
  },
  script: {
    upload: script => ({ type: 'UPLOAD_SCRIPT', script }),
    save: script => {
      const exported = exportScript(script)
      api.spec.upsert(exported)
        // .then(() => console.warn('it worked!'))
        // .catch(() => console.warn('it failed!'))
      return {type: 'NULL_OP'}
    }
  },
}
