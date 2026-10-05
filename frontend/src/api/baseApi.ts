import {
  createApi,
  FetchBaseQueryError,
  fetchBaseQuery,
  retry,
} from '@reduxjs/toolkit/query/react'

const MAX_RETRIES = 2

const getCookie = (name) => {
  const value = `; ${document.cookie}`
  const parts = value.split(`; ${name}=`)
  if (parts.length === 2) {
    return parts[1].split(';')[0]
  }
}

const baseQuery = fetchBaseQuery({
  baseUrl: '/',

  prepareHeaders: (headers) => {
    const csrfToken = getCookie('csrftoken')
    if (csrfToken) {
      headers.set('x-csrftoken', csrfToken)
    }
    return headers
  },
})

// Retry queries whose request never completed (a dropped connection). Mutations
// are not retried as they may not be idempotent, and an HTTP error response is a
// real answer.
const baseQueryWithRetry = retry(baseQuery, {
  retryCondition: (error, _args, { attempt, baseQueryApi }) =>
    baseQueryApi.type === 'query' &&
    !baseQueryApi.signal.aborted &&
    (error as FetchBaseQueryError).status === 'FETCH_ERROR' &&
    attempt <= MAX_RETRIES,
})

export const baseApi = createApi({
  baseQuery: baseQueryWithRetry,
  endpoints: () => ({}),
  tagTypes: [],
})
