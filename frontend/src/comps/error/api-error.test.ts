import { describe, expect, it } from 'vitest'
import { ApiRequestError, isServerError, toReportableError } from './api-error'

describe('isServerError', () => {
  const errorPage = (originalStatus: number) => ({
    status: 'PARSING_ERROR',
    originalStatus,
    data: '<html></html>',
    error: 'SyntaxError: Unexpected token <',
  })

  it.each([
    ['an HTTP 500', { status: 500, data: {} }],
    ['an HTTP 503', { status: 503, data: {} }],
    ['the maintenance page, which nginx serves as a 500', errorPage(500)],
    ['a Cloudflare 522 page', errorPage(522)],
  ])('is true for %s', (_, thrown) => {
    expect(isServerError(thrown)).toBe(true)
  })

  it.each([
    ['an HTTP 404', { status: 404, data: {} }],
    ['an HTTP 400', { status: 400, data: {} }],
    ['a request that never completed', { status: 'FETCH_ERROR', error: 'x' }],
    [
      'a body that failed to download',
      { status: 'PARSING_ERROR', originalStatus: 200, data: '', error: 'x' },
    ],
    ['a real error', new Error('boom')],
    ['a string', 'boom'],
    ['null', null],
  ])('is false for %s', (_, thrown) => {
    expect(isServerError(thrown)).toBe(false)
  })
})

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
