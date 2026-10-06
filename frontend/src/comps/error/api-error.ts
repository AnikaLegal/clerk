import { FetchBaseQueryError } from '@reduxjs/toolkit/query/react'

export class ApiRequestError extends Error {
  constructor(description: string) {
    super(`API request failed: ${description}`)
    this.name = 'ApiRequestError'
  }
}

const isQueryError = (thrown: unknown): thrown is FetchBaseQueryError =>
  typeof thrown === 'object' &&
  thrown !== null &&
  'status' in thrown &&
  (typeof thrown.status === 'number' || typeof thrown.status === 'string')

const describe = (error: FetchBaseQueryError) => {
  if (typeof error.status === 'number') {
    return `HTTP ${error.status}`
  }
  if (error.status === 'PARSING_ERROR') {
    return `${error.status} (HTTP ${error.originalStatus})`
  }
  return error.status
}

// Pages throw an RTK Query error as the plain object it is, which Sentry can
// only report as "Object captured as exception". Give those a real error with a
// readable message and leave anything else as it was.
export const toReportableError = (thrown: unknown): unknown =>
  isQueryError(thrown) ? new ApiRequestError(describe(thrown)) : thrown
