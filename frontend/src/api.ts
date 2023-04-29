import { Person, CreatePerson } from 'types'
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

interface HandledResponse<T> {
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
  contact: {
    create: (contact) => {
      const url = `/closed-contact/`
      return http.post(url, contact)
    },
  },
  person: {
    list: () => {
      const url = '/clerk/parties/'
      return http.get<Person[]>(url)
    },
    search: (query: any) => {
      const url = '/clerk/parties/search/'
      return http.get<Person[]>(url, query)
    },
    create: (data: CreatePerson) => {
      const url = '/clerk/parties/create/'
      return http.post<Person>(url, data)
    },
    update: (pk: number, data: Partial<CreatePerson>) => {
      const url = `/clerk/parties/${pk}/`
      return http.put<Person>(url, data)
    },
    delete: (pk: number) => {
      const url = `/clerk/parties/${pk}/`
      return http.delete<{}>(url)
    },
  },
  client: {
    update: (clientId, client) => {
      const url = `/clerk/client/${clientId}/`
      return http.patch(url, client)
    },
  },
  case: {
    docs: (caseId) => {
      const url = `/clerk/cases/${caseId}/docs/sharepoint/`
      return http.get(url)
    },
    search: (query) => {
      const url = `/clerk/cases/`
      return http.get(url, query)
    },
    update: (caseId, issue) => {
      const url = `/clerk/cases/detail/${caseId}/update/`
      return http.post(url, issue)
    },
    // Assign a paralegal + lawyer
    assign: (caseId, issue) => {
      const url = `/clerk/cases/detail/${caseId}/assign/`
      return http.post(url, issue)
    },
    note: {
      add: (caseId, note) => {
        const url = `/clerk/cases/detail/${caseId}/note/`
        return http.post(url, note)
      },
    },
    supportWorker: {
      add: (caseId, supportWorkerId) => {
        const url = `/clerk/cases/detail/${caseId}/support-worker/`
        return http.post(url, { person_id: supportWorkerId })
      },
      remove: (caseId) => {
        const url = `/clerk/cases/detail/${caseId}/support-worker/`
        return http.delete(url)
      },
    },
    agent: {
      add: (caseId, agentId) => {
        const url = `/clerk/cases/detail/${caseId}/agent/`
        return http.post(url, { person_id: agentId })
      },
      remove: (caseId) => {
        const url = `/clerk/cases/detail/${caseId}/agent/`
        return http.delete(url)
      },
    },
    landlord: {
      add: (caseId, landlordId) => {
        const url = `/clerk/cases/detail/${caseId}/landlord/`
        return http.post(url, { person_id: landlordId })
      },
      remove: (caseId) => {
        const url = `/clerk/cases/detail/${caseId}/landlord/`
        return http.delete(url)
      },
    },
  },
  email: {
    create: (issueId, email) => {
      const url = `/clerk/cases/email/${issueId}/draft/`
      return http.post(url, email)
    },
    update: (issueId, emailId, data) => {
      const url = `/clerk/cases/email/${issueId}/draft/${emailId}/`
      return http.patch(url, data)
    },
    send: (issueId, emailId) => {
      const url = `/clerk/cases/email/${issueId}/draft/${emailId}/send/`
      return http.post(url, {})
    },
    delete: (issueId, emailId) => {
      const url = `/clerk/cases/email/${issueId}/draft/${emailId}/`
      return http.delete(url)
    },
    attachment: {
      create: (issueId, emailId, attachment) => {
        const url = `/clerk/cases/email/${issueId}/draft/${emailId}/attachment/`
        return http.post(url, attachment, {
          'Content-Type': 'multipart/form-data',
        })
      },
      createFromSharepoint: (issueId, emailId, sharepointId) => {
        const url = `/clerk/cases/email/${issueId}/draft/${emailId}/attachment/`
        return http.post(url, { sharepoint_id: sharepointId })
      },
      delete: (issueId, emailId, attachId) => {
        const url = `/clerk/cases/email/${issueId}/draft/${emailId}/attachment/${attachId}/`
        return http.delete(url)
      },
      // Upload email attachment to sharepoint
      upload: (issuePk, emailPk, attachId) => {
        const url = `/clerk/cases/email/${issuePk}/${emailPk}/${attachId}/`
        return http.post(url, {})
      },
    },
  },
  accounts: {
    update: (accountId, account) => {
      const url = `/clerk/accounts/user/${accountId}/`
      return http.patch(url, account)
    },
    getPermissions: (accountId) => {
      const url = `/clerk/accounts/user/${accountId}/perms/`
      return http.get(url)
    },
    search: (query) => {
      const url = '/clerk/accounts/'
      return http.get(url, query)
    },
    promote: (accountId) => {
      const url = `/clerk/accounts/user/${accountId}/perms/promote/`
      return http.post(url)
    },
    demote: (accountId) => {
      const url = `/clerk/accounts/user/${accountId}/perms/demote/`
      return http.post(url)
    },
    resync: (accountId) => {
      const url = `/clerk/accounts/user/${accountId}/perms/resync/`
      return http.post(url)
    },
  },
  templates: {
    notify: {
      search: (query) => {
        const url = '/clerk/templates/notify/search/'
        return http.get(url, query)
      },
      create: (data) => {
        const url = '/clerk/templates/notify/create/'
        return http.post(url, data)
      },
      update: (pk, data) => {
        const url = `/clerk/templates/notify/${pk}/`
        return http.put(url, data)
      },
      delete: (pk) => {
        const url = `/clerk/templates/notify/${pk}/delete/`
        return http.delete(url)
      },
    },
    doc: {
      search: (query) => {
        const url = '/clerk/templates/doc/search/'
        return http.get(url, query)
      },
      delete: (pk) => {
        const url = `/clerk/templates/doc/${pk}/delete/`
        return http.delete(url)
      },
    },
    email: {
      search: (query) => {
        const url = '/clerk/templates/email/search/'
        return http.get(url, query)
      },
      create: (data) => {
        const url = '/clerk/templates/email/create/'
        return http.post(url, data)
      },
      update: (pk, data) => {
        const url = `/clerk/templates/email/${pk}/`
        return http.put(url, data)
      },
      delete: (pk) => {
        const url = `/clerk/templates/email/${pk}/`
        return http.delete(url)
      },
    },
  },
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
