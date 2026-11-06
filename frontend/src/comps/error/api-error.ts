import { FetchBaseQueryError } from '@reduxjs/toolkit/query/react'

const DIGIT_NAMES = [
  'zero',
  'one',
  'two',
  'three',
  'four',
  'five',
  'six',
  'seven',
  'eight',
  'nine',
]

// Sentry replaces numbers in a fingerprint with a placeholder, which would put
// every HTTP status in one issue, so the digits are spelled out.
const spellNumbers = (text: string) =>
  text.replace(/\d+/g, (digits) =>
    [...digits].map((digit) => DIGIT_NAMES[Number(digit)]).join('-')
  )

export class ApiRequestError extends Error {
  // These errors share the error boundary's stack, so they are grouped by
  // what failed instead.
  readonly fingerprint: string[]

  constructor(description: string) {
    super(`API request failed: ${description}`)
    this.name = 'ApiRequestError'
    this.fingerprint = ['ApiRequestError', spellNumbers(description)]
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

// A server error, or an error page from the proxy or CDN in front of it.
export const isServerError = (thrown: unknown) => {
  if (!isQueryError(thrown)) {
    return false
  }
  const status =
    thrown.status === 'PARSING_ERROR' ? thrown.originalStatus : thrown.status
  return typeof status === 'number' && status >= 500
}

// Pages throw an RTK Query error as the plain object it is, which Sentry can
// only report as "Object captured as exception". Give those a real error with a
// readable message and leave anything else as it was.
export const toReportableError = (thrown: unknown): unknown =>
  isQueryError(thrown) ? new ApiRequestError(describe(thrown)) : thrown
