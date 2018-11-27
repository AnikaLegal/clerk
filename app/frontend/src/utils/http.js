import Cookies from 'universal-cookie'

// Get Django cross site request forgery cookie for API requests.
const getCSRF = () => new Cookies().get('csrftoken')

// HTTP helper functions.
const http = {
  // POST a JSON to URL (create new resource)
  post: (url, data) =>
    fetch(url, {
      method: 'POST',
      credentials: 'include',
      body: JSON.stringify(data),
      headers: {
        'X-CSRFToken': getCSRF(),
        'Content-Type': 'application/json',
      },
    }),
  // PATCH a JSON to URL (partially update resource)
  patch: (url, data) =>
    fetch(url, {
      method: 'PATCH',
      credentials: 'include',
      body: JSON.stringify(data),
      headers: {
        'X-CSRFToken': getCSRF(),
        'Content-Type': 'application/json',
      },
    }),
  // PUT a JSON to URL (fully update resource)
  put: (url, data) =>
    fetch(url, {
      method: 'PUT',
      credentials: 'include',
      body: JSON.stringify(data),
      headers: {
        'X-CSRFToken': getCSRF(),
        'Content-Type': 'application/json',
      },
    }),
  // DELETE a URL (delete resource)
  delete: url =>
    fetch(url, {
      method: 'DELETE',
      credentials: 'include',
      headers: { 'X-CSRFToken': getCSRF() },
    }),
  // GET a URL (read resource)
  get: url =>
    fetch(url, {
      credentials: 'include',
    }),
}

export default http
