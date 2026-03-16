import { Upload, Submission } from 'intake/types'

const getCookie = (name) => {
  const value = `; ${document.cookie}`
  const parts = value.split(`; ${name}=`)
  if (parts.length === 2) {
    return parts.pop().split(';').shift()
  }
}

const BASE_CONFIG = {
  method: null,
  credentials: 'include',
  headers: {
    'X-React': 'true',
    'X-CSRFToken': getCookie('csrftoken'),
    'Content-Type': 'application/json',
  },
}

export interface HandledResponse<T> {
  resp: Response
  data: T | null
  errors: { [key: string]: any } | null
}

const handleResponse = async <T>(
  resp: Response
): Promise<HandledResponse<T>> => {
  let data = null
  let errors = null
  if (resp.ok && resp.status !== 204) {
    try {
      data = await resp.json()
    } catch {
      console.error('Could not parse response JSON.')
    }
  }
  if (!resp.ok) {
    try {
      errors = await resp.json()
    } catch {
      console.error('Could not parse response JSON.')
    }
  }
  return { resp, data, errors }
}

const sendData = async <T>(
  url: string,
  data: any,
  method: string,
  headers = {}
): Promise<HandledResponse<T>> => {
  const config = {
    ...BASE_CONFIG,
    headers: { ...BASE_CONFIG.headers, ...headers },
    method: method,
    body: undefined,
  }
  if (config.headers['Content-Type'] === 'application/json') {
    config.body = JSON.stringify(data)
  } else if (config.headers['Content-Type'] === 'multipart/form-data') {
    config.body = new FormData()
    for (let [k, v] of Object.entries(data)) {
      if (Array.isArray(v) && v.length === 0) {
        continue
      } else {
        config.body.append(k, v)
      }
    }
    delete config.headers['Content-Type']
  }
  const resp = await fetch(url, config as any)
  return handleResponse<T>(resp)
}

const http = {
  post: <T>(url, data = {}, headers = {}): Promise<HandledResponse<T>> =>
    sendData(url, data, 'POST', headers),
  patch: <T>(url, data, headers = {}): Promise<HandledResponse<T>> =>
    sendData(url, data, 'PATCH', headers),
  put: <T>(url, data, headers = {}): Promise<HandledResponse<T>> =>
    sendData(url, data, 'PUT', headers),
  get: async <T>(url, query?): Promise<HandledResponse<T>> => {
    let finalURL = url
    if (query) {
      const qs = new URLSearchParams(query).toString()
      finalURL = `${url}?${qs}`
    }
    const config = { ...BASE_CONFIG, method: 'GET' }
    const resp = await fetch(finalURL, config as any)
    return handleResponse(resp)
  },
  delete: async <T>(url): Promise<HandledResponse<T>> => {
    const config = { ...BASE_CONFIG, method: 'DELETE' }
    const resp = await fetch(url, config as any)
    return handleResponse(resp)
  },
}

export const api = {
  // Client intake form
  intake: {
    // Upload a new file upload to a submission.
    upload: async (file: File): Promise<Upload> => {
      const url = '/api/upload/'
      const form = new FormData()
      form.append('file', file)
      const request = { method: 'POST', body: form }
      const resp = await fetch(url, request)
      // Handle case where user tries to upload corrupt image,
      // or renames their PDF to mydoc.png and tries to upload that.
      if (resp.status == 400) {
        throw 400
      }
      const data = await resp.json()
      return data
    },
    submission: {
      // Create a new submission.
      get: async (id: string) => {
        const url = `/api/submission/${id}/`
        return await http.get<Submission>(url)
      },
      // Create a new submission.
      create: async (answers: Object) => {
        const url = '/api/submission/'
        return await http.post<Submission>(url, { answers })
      }, // Create a new submission.
      update: async (id: string, answers: Object) => {
        const url = `/api/submission/${id}/`
        return await http.patch<Submission>(url, { answers })
      }, // Create a new submission.
      submit: async (id: string) => {
        const url = `/api/submission/${id}/submit/`
        return await http.post<void>(url, {})
      },
    },
  },
}
