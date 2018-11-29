import camelize from 'camelize'

// Default error message for when a HTTP request fails
const DEFAULT_ERROR_MESSAGE =
  "Something's gone wrong with your request. Try reloading the page and try again. " +
  "If that doesn't help, then contact the tech team at webmaster@anikalegal.com"

// Recursively convert snake_case to camelCase.
const parsePythonObject = obj => {
  if (Array.isArray(obj)) {
    return obj.map(parsePythonObject)
  } else if (typeof obj === 'object') {
    return camelize(obj)
  }
  return obj
}

// Check for an error in an API request - write appropriate message to redux store.
// Errors should always have the form { name: [msg, msg], name: [msg] }
const checkForError = dispatch => response => {
  let errorMessage = DEFAULT_ERROR_MESSAGE
  if (response.status === 400) {
    // Bad request, try and get details
    errorMessage = 'Bad request - invalid data.'
    response
      .json()
      .then(errorData => dispatch({ type: 'WRITE_ERROR', errors: errorData }))
  } else if (response.status === 401 || response.status === 403) {
    errorMessage = 'Forbidden - you do not have permission to do this.'
  }
  if (response.status >= 400) {
    console.error(response.status, response.statusText) // eslint-disable-line no-console
    dispatch({ type: 'WRITE_ERROR', errors: { error: [errorMessage] } })
    throw new Error(`HTTP API error: ${response.status}`)
  }
  return response
}

// Handle response from a JSON HTTP API, returns a promise of a JS object.
const handleJSONResponse = dispatch => response => {
  checkForError(dispatch)(response)
  return response.json().then(parsePythonObject)
}

// Handle an API error in a catch block - displays an error modal
const handleError = dispatch => error => {
  console.error(error) // eslint-disable-line no-console
  dispatch({ type: 'SHOW_ERROR' })
}

export { checkForError, handleJSONResponse, handleError }
