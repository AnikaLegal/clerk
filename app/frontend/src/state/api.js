// import Cookies from 'universal-cookie'

// const getCSRF = () => new Cookies().get('csrftoken')

const URL = 'http://localhost:5000/insert/specs/'

const postJSON = (url, json) =>
  fetch(url, {
    method: 'POST',
    credentials: 'include',
    body: JSON.stringify(json),
    headers: {
      // 'X-CSRFToken': getCSRF(),
      'Content-Type': 'application/json',
    },
  })

const get = url =>
  fetch(url, { method: 'GET' })


const insert = (table, data) =>
  postJSON(`http://localhost:5000/insert/${table}`, data)


const list = table =>
  get(`http://localhost:5000/${table}`)


// NB. this isn't used anywhere yet.
export default {
  answer: {
    list: () =>
      list('answers'),
    insert: answers =>
      insert('answers', answers),
  },
  script: {
    list: () =>
      list('scripts'),
    insert: script =>
      insert('scripts', script),
  },
}
