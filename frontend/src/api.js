import { URLS } from 'consts'

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

const handleResponse = async (resp) => {
  let data = {}
  if (resp.status !== 204) {
    try {
      data = await resp.json()
    } catch {
      console.error('Could not parse response JSON.')
    }
  }
  return { resp, data }
}

const sendData = async (url, data, method, headers = {}) => {
  const config = {
    ...BASE_CONFIG,
    headers: { ...BASE_CONFIG.headers, ...headers },
    method: method,
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
  const resp = await fetch(url, config)
  return handleResponse(resp)
}

const http = {
  post: (url, data, headers = {}) => sendData(url, data, 'POST', headers),
  patch: (url, data, headers = {}) => sendData(url, data, 'PATCH', headers),
  put: (url, data, headers = {}) => sendData(url, data, 'PUT', headers),
  get: async (url, query) => {
    let finalURL = url
    if (query) {
      const qs = new URLSearchParams(query).toString()
      finalURL = `${url}?${qs}`
    }
    const config = { ...BASE_CONFIG, method: 'GET' }
    const resp = await fetch(finalURL, config)
    return handleResponse(resp)
  },
  delete: async (url) => {
    const config = { ...BASE_CONFIG, method: 'DELETE' }
    const resp = await fetch(url, config)
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
      return http.get(URLS.PERSON.LIST)
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
      return http.get(URLS.ACCOUNTS.SEARCH, query)
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
    },
  },
}
