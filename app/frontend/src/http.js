const CSRFToken = window.CSRFToken || ''

// HTTP helper functions.
export const http = {
  // POST a JSON to URL (create new resource)
  post: async (path, data) => {
    const resp = await fetch(path, {
      method: 'POST',
      credentials: 'include',
      body: serializeBody(data),
      headers: {
        'X-CSRFToken': CSRFToken,
        'Content-Type': 'application/json',
      },
    })
    return handleResponse(resp)
  },
  // PATCH a JSON to URL (partially update resource)
  patch: async (path, data) => {
    const resp = await fetch(path, {
      method: 'PATCH',
      credentials: 'include',
      body: serializeBody(data),
      headers: {
        'X-CSRFToken': CSRFToken,
        'Content-Type': 'application/json',
      },
    })
    return handleResponse(resp)
  },
  // PUT a JSON to URL (fully update resource)
  put: async (path, data) => {
    const resp = await fetch(path, {
      method: 'PUT',
      credentials: 'include',
      body: serializeBody(data),
      headers: {
        'X-CSRFToken': CSRFToken,
        'Content-Type': 'application/json',
      },
    })
    return handleResponse(resp)
  },
  // DELETE a URL (delete resource)
  delete: async (path) => {
    const resp = await fetch(path, {
      method: 'DELETE',
      credentials: 'include',
      headers: { 'X-CSRFToken': CSRFToken },
    })
    return handleResponse(resp)
  },
  // GET a URL (read resource)
  get: async (path) => {
    const resp = await fetch(path, { credentials: 'include' })
    return handleResponse(resp)
  },
}

const serializeBody = (data) => {
  if (data.constructor === FormData) {
    return data
  } else {
    return JSON.stringify(data)
  }
}

const handleResponse = async (resp) => {
  if (!resp.ok) {
    // The HTTP request failed.
    let error
    try {
      // Try parse the response data anyway.
      const data = await resp.json()
      error = { resp, data }
    } catch {
      // Couldn't parse response, just throw the request.
      error = { resp }
    }
    throw error
  }
  if (resp.status === 204) {
    // Django DELETE returns no content,
    // So we shouldn't try parse the response data.
    return {}
  }
  try {
    // Try to parse the response data.
    const data = await resp.json()
    return data
  } catch (error) {
    // Parsing the response failed.
    throw error
  }
}
