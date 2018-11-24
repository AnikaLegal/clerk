export default {
  question: {
    create: () => {
      const randomString = Math.random()
        .toString(36)
        .substring(4)
        .toUpperCase()
      const id = randomString
      return { type: 'CREATE_QUESTION', id }
    },
    update: (question) => ({ type: 'UPDATE_QUESTION', question }),
    remove: id => ({ type: 'REMOVE_QUESTION', id }),
  },
  script: {
    upload: script => ({ type: 'UPLOAD_SCRIPT', script }),
  },
}
