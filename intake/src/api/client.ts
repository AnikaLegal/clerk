export interface ApiError {
  status: number
  data?: unknown
}

const getCookie = (name: string): string | undefined => {
  const value = `; ${document.cookie}`
  const parts = value.split(`; ${name}=`)
  if (parts.length === 2) return parts.pop()?.split(';').shift()
}

// Anonymous visitors POST without CSRF (SessionAuthentication only enforces
// it for session-authenticated users), but logged-in staff filling the form
// would 403 without the token, so send it whenever the cookie exists.
const baseHeaders = (): Record<string, string> => {
  const headers: Record<string, string> = {}
  const csrfToken = getCookie('csrftoken')
  if (csrfToken) {
    headers['x-csrftoken'] = csrfToken
  }
  return headers
}

const handleResponse = async (resp: Response): Promise<unknown> => {
  if (!resp.ok) {
    let error: ApiError
    try {
      error = { status: resp.status, data: await resp.json() }
    } catch {
      error = { status: resp.status }
    }
    // Don't report here: some non-2xx responses are expected and handled by
    // the caller (a 403 already_submitted is treated as success in
    // SubmissionSaver.submit; 403/404 are start-from-scratch in ResumePage).
    // Every caller logs genuinely unexpected failures itself, so reporting
    // here would only double-count and bury real 500s under handled noise.
    throw error
  }
  if (resp.status === 204) {
    return {}
  }
  return await resp.json()
}

export const http = {
  get: async (url: string): Promise<unknown> => {
    const resp = await fetch(url, { headers: baseHeaders() })
    return handleResponse(resp)
  },
  post: async (url: string, data: object): Promise<unknown> => {
    const resp = await fetch(url, {
      method: 'POST',
      body: JSON.stringify(data),
      headers: { ...baseHeaders(), 'Content-Type': 'application/json' },
    })
    return handleResponse(resp)
  },
  patch: async (url: string, data: object): Promise<unknown> => {
    const resp = await fetch(url, {
      method: 'PATCH',
      body: JSON.stringify(data),
      // Let an answers PATCH ride out page teardown (the tab-close flush).
      // Keepalive bodies are capped at 64KB; the per-question input caps keep
      // answer payloads far below that.
      keepalive: true,
      headers: { ...baseHeaders(), 'Content-Type': 'application/json' },
    })
    return handleResponse(resp)
  },
  postMultipart: async (url: string, form: FormData): Promise<unknown> => {
    const resp = await fetch(url, {
      method: 'POST',
      body: form,
      headers: baseHeaders(),
    })
    return handleResponse(resp)
  },
}
