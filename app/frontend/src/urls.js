// All URLs used in the frontend.

// API endpoints
const API = {
  SCRIPT: '/api/questions/script/',
  QUESTION: '/api/questions/question/',
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
    },
  },
  client: {
    script: {
      list: () => CLIENT.SCRIPT,
      details: id => `${CLIENT.SCRIPT}${id}/`,
    },
  },
}

export default urls
