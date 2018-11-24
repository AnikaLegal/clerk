// import Cookies from 'universal-cookie'

// import { API } from 'consts';

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


// NB. this isn't used anywhere yet.
export default {
  spec: {
    upsert: script =>
      postJSON(URL, script)
  },
}
