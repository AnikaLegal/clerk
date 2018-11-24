import uniqid from 'uniqid'

import { api } from 'state' 

export default {
  question: {
    create: () => {
      return { type: 'CREATE_QUESTION', id: `${uniqid()}-${uniqid()}` }
    },
    update: (question) => ({ type: 'UPDATE_QUESTION', question }),
    remove: id => ({ type: 'REMOVE_QUESTION', id }),
  },
  script: {
    upload: script => ({ type: 'UPLOAD_SCRIPT', script }),
    save: script => {
      api.spec.upsert(Object.values(script))
        // .then(() => console.warn('it worked!'))
        // .catch(() => console.warn('it failed!'))
      return {type: 'NULL_OP'}
    }
  },
}
