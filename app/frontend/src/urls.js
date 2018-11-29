// All URLs used in the frontend.

// API endpoints
const API = {
  SCRIPT: '/api/questions/script/',
  QUESTION: '/api/questions/question/',
  TRANSITION: '/api/questions/transition/',
}
// User facing endpoints
const CLIENT = {
  SCRIPT: '/questionnaire/',
}

// URL builder functions.
const urls = {
  api: {
    script: {
      list: () => API.SCRIPT,
      details: id => `${API.SCRIPT}${id}/`,
    },
    question: {
      list: () => API.QUESTION,
      details: id => `${API.QUESTION}${id}/`,
    },
    transition: {
      list: () => API.TRANSITION,
      details: id => `${API.TRANSITION}${id}/`,
    },
  },
  client: {
    script: {
      list: () => CLIENT.SCRIPT,
      details: id => `${CLIENT.SCRIPT}${id}/`,
      graph: id => `${CLIENT.SCRIPT}${id}/view/`,
      test: id => `${CLIENT.SCRIPT}${id}/test/`,
    },
  },
}

export default urls
