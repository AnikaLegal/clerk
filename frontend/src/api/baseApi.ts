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

// A response whose headers arrived but whose body did not (a dropped connection)
// comes back as a parsing error with no body.
const isDroppedBody = (error: FetchBaseQueryError) =>
  error.status === 'PARSING_ERROR' && error.originalStatus < 400 && !error.data

// Retry queries whose request or response body never completed (a dropped
// connection). Mutations are not retried as they may not be idempotent, and an
// HTTP error response is a real answer.
const baseQueryWithRetry = retry(baseQuery, {
  retryCondition: (error, _args, { attempt, baseQueryApi }) => {
    const fetchError = error as FetchBaseQueryError
    return (
      baseQueryApi.type === 'query' &&
      !baseQueryApi.signal.aborted &&
      (fetchError.status === 'FETCH_ERROR' || isDroppedBody(fetchError)) &&
      attempt <= MAX_RETRIES
    )
  },
})

export const baseApi = createApi({
  baseQuery: baseQueryWithRetry,
  endpoints: () => ({}),
  tagTypes: [],
})
