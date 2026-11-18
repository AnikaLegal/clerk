import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { http } from '../src/api/client'

const fetchMock = vi.fn()

const csrfHeaderSent = async (cookie: string) => {
  vi.stubGlobal('document', { cookie })
  await http.get('/api/thing/')
  const [, init] = fetchMock.mock.calls[0]
  return init.headers['x-csrftoken']
}

describe('CSRF header', () => {
  beforeEach(() => {
    fetchMock.mockReset()
    fetchMock.mockResolvedValue(new Response('{}', { status: 200 }))
    vi.stubGlobal('fetch', fetchMock)
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('sends the token from the csrftoken cookie', async () => {
    expect(await csrfHeaderSent('other=1; csrftoken=abc123')).toBe('abc123')
  })

  it('prefers the __Host-csrftoken cookie', async () => {
    expect(
      await csrfHeaderSent('csrftoken=stale; __Host-csrftoken=current')
    ).toBe('current')
  })

  it('sends no header when there is no CSRF cookie', async () => {
    expect(await csrfHeaderSent('other=1')).toBeUndefined()
  })
})
