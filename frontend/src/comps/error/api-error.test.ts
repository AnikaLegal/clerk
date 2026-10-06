import { describe, expect, it } from 'vitest'
import { ApiRequestError, toReportableError } from './api-error'

describe('toReportableError', () => {
  it('turns a network failure into a readable error', () => {
    const result = toReportableError({
      status: 'FETCH_ERROR',
      error: 'TypeError: Failed to fetch',
    })
    expect(result).toBeInstanceOf(ApiRequestError)
    expect(result).toBeInstanceOf(Error)
    expect(result).toMatchObject({
      name: 'ApiRequestError',
      message: 'API request failed: FETCH_ERROR',
    })
  })

  it('names the HTTP status of an error response', () => {
    expect(toReportableError({ status: 404, data: {} })).toMatchObject({
      message: 'API request failed: HTTP 404',
    })
  })

  it('names the HTTP status of a response that could not be parsed', () => {
    const maintenancePage = {
      status: 'PARSING_ERROR',
      originalStatus: 500,
      data: '<html></html>',
      error: 'SyntaxError: Unexpected token <',
    }
    expect(toReportableError(maintenancePage)).toMatchObject({
      message: 'API request failed: PARSING_ERROR (HTTP 500)',
    })
  })

  it('keeps the message free of anything from the response body', () => {
    const result = toReportableError({
      status: 400,
      data: { errors: [{ detail: 'Jane Citizen is not a valid client' }] },
    }) as Error
    expect(result.message).not.toContain('Jane')
  })

  it('leaves a real error as it was', () => {
    const error = new Error('boom')
    expect(toReportableError(error)).toBe(error)
  })

  it.each([
    ['a string', 'boom'],
    ['an object with no status', { message: 'boom' }],
    ['null', null],
  ])('leaves %s as it was', (_, thrown) => {
    expect(toReportableError(thrown)).toBe(thrown)
  })
})
