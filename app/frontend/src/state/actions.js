export default {
  question: {
    create: () => {
      const randomString = Math.random().toString(36).substring(4).toUpperCase()
      const name = `New Question ${randomString}`
      return {type: 'CREATE_QUESTION', name}
    },
    update: (prevName, question) => ({type: 'UPDATE_QUESTION', question, prevName}),
    remove: (name) => (({type: 'REMOVE_QUESTION', name}))
  },
  script: {
    upload: script => ({type: 'UPLOAD_SCRIPT', script}),
  }
}
