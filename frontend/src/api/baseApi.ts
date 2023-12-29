import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'

const getCookie = (name) => {
  const value = `; ${document.cookie}`
  const parts = value.split(`; ${name}=`)
  if (parts.length === 2) {
    return parts.pop().split(';').shift()
  }
}

export const baseApi = createApi({
  baseQuery: fetchBaseQuery({
    baseUrl: '/',

    prepareHeaders: (headers, { getState }) => {
      const csrfToken = getCookie('csrftoken')
      if (csrfToken) {
        headers.set('x-csrftoken', csrfToken)
      }
      return headers
    },
  }),
  endpoints: () => ({}),
  tagTypes: [],
})
