import Cookies from 'universal-cookie'

// import { API } from 'consts';

const getCSRF = () => new Cookies().get('csrftoken')

const postJSON = (url, json) =>
  fetch(url, {
    method: 'POST',
    credentials: 'include',
    body: JSON.stringify(json),
    headers: {
      'X-CSRFToken': getCSRF(),
      'Content-Type': 'application/json',
    },
  })

// NB. this isn't used anywhere yet.
export default {
  validate: {
    // post: script =>
    // postJSON(API.VALIDATE, { script })
  },
}
