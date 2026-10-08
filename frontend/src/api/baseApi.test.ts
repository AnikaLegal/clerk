import { configureStore } from '@reduxjs/toolkit'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { baseApi } from './baseApi'

const api = baseApi.injectEndpoints({
  endpoints: (build) => ({
    getThing: build.query<{ ok: boolean }, void>({
      query: () => 'http://localhost/thing',
    }),
    saveThing: build.mutation<{ ok: boolean }, void>({
      query: () => ({ url: 'http://localhost/thing', method: 'POST' }),
    }),
  }),
})

const makeStore = () =>
  configureStore({
    reducer: { [api.reducerPath]: api.reducer },
    middleware: (getDefaultMiddleware) =>
      getDefaultMiddleware().concat(api.middleware),
  })

const json = (status: number, body: unknown) =>
  new Response(JSON.stringify(body), {
    status,
    headers: { 'content-type': 'application/json' },
  })

const networkError = () => new TypeError('Failed to fetch')

// A response whose body stream fails part way, like a connection dropped
// mid-download.
const droppedBody = (status = 200) =>
  new Response(
    new ReadableStream({
      start: (controller) => controller.error(networkError()),
    }),
    { status }
  )

// Lets every retry backoff elapse so a test can await the final result.
const settle = async <T>(request: PromiseLike<T>) => {
  await vi.advanceTimersByTimeAsync(10_000)
  return request
}

describe('baseApi', () => {
  const fetchMock = vi.fn()

  beforeEach(() => {
    vi.useFakeTimers()
    fetchMock.mockReset()
    vi.stubGlobal('fetch', fetchMock)
    vi.stubGlobal('document', { cookie: '' })
  })

  afterEach(() => {
    vi.useRealTimers()
    vi.unstubAllGlobals()
  })

  describe('CSRF header', () => {
    it('sends the token from the csrftoken cookie', async () => {
      vi.stubGlobal('document', { cookie: 'other=1; csrftoken=abc123; x=y' })
      fetchMock.mockResolvedValue(json(200, { ok: true }))
      await settle(makeStore().dispatch(api.endpoints.getThing.initiate()))
      const [request] = fetchMock.mock.calls[0]
      expect(request.headers.get('x-csrftoken')).toBe('abc123')
    })

    it('sends no header when there is no csrftoken cookie', async () => {
      vi.stubGlobal('document', { cookie: 'other=1' })
      fetchMock.mockResolvedValue(json(200, { ok: true }))
      await settle(makeStore().dispatch(api.endpoints.getThing.initiate()))
      const [request] = fetchMock.mock.calls[0]
      expect(request.headers.get('x-csrftoken')).toBeNull()
    })
  })

  describe('retries', () => {
    it('retries a query that fails with a network error', async () => {
      fetchMock
        .mockRejectedValueOnce(networkError())
        .mockRejectedValueOnce(networkError())
        .mockResolvedValueOnce(json(200, { ok: true }))
      const result = await settle(
        makeStore().dispatch(api.endpoints.getThing.initiate())
      )
      expect(result.data).toEqual({ ok: true })
      expect(fetchMock).toHaveBeenCalledTimes(3)
    })

    it('gives up after two retries', async () => {
      fetchMock.mockRejectedValue(networkError())
      const result = await settle(
        makeStore().dispatch(api.endpoints.getThing.initiate())
      )
      expect(result.error).toMatchObject({ status: 'FETCH_ERROR' })
      expect(fetchMock).toHaveBeenCalledTimes(3)
    })

    it('does not retry an HTTP error response', async () => {
      fetchMock.mockResolvedValue(json(500, { detail: 'boom' }))
      const result = await settle(
        makeStore().dispatch(api.endpoints.getThing.initiate())
      )
      expect(result.error).toMatchObject({ status: 500 })
      expect(fetchMock).toHaveBeenCalledTimes(1)
    })

    it('does not retry a mutation that fails with a network error', async () => {
      fetchMock.mockRejectedValue(networkError())
      const result = await settle(
        makeStore().dispatch(api.endpoints.saveThing.initiate())
      )
      expect(result.error).toMatchObject({ status: 'FETCH_ERROR' })
      expect(fetchMock).toHaveBeenCalledTimes(1)
    })

    it('does not retry a request that was aborted', async () => {
      // Like a real fetch, reject when the request's signal aborts.
      fetchMock.mockImplementation(
        (request: Request) =>
          new Promise((_, reject) => {
            request.signal.addEventListener('abort', () =>
              reject(networkError())
            )
          })
      )
      const request = makeStore().dispatch(api.endpoints.getThing.initiate())
      await vi.waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1))
      request.abort()
      await settle(request)
      expect(fetchMock).toHaveBeenCalledTimes(1)
    })
  })

  describe('a response whose body fails to download', () => {
    it('retries a query', async () => {
      fetchMock
        .mockResolvedValueOnce(droppedBody())
        .mockResolvedValueOnce(json(200, { ok: true }))
      const result = await settle(
        makeStore().dispatch(api.endpoints.getThing.initiate())
      )
      expect(result.data).toEqual({ ok: true })
      expect(fetchMock).toHaveBeenCalledTimes(2)
    })

    it('gives up after two retries', async () => {
      fetchMock.mockImplementation(async () => droppedBody())
      const result = await settle(
        makeStore().dispatch(api.endpoints.getThing.initiate())
      )
      expect(result.error).toMatchObject({ status: 'PARSING_ERROR' })
      expect(fetchMock).toHaveBeenCalledTimes(3)
    })

    it('is not retried when the response was an error status', async () => {
      fetchMock.mockImplementation(async () => droppedBody(500))
      const result = await settle(
        makeStore().dispatch(api.endpoints.getThing.initiate())
      )
      expect(result.error).toMatchObject({
        status: 'PARSING_ERROR',
        originalStatus: 500,
      })
      expect(fetchMock).toHaveBeenCalledTimes(1)
    })

    it('is not retried for a mutation, which may have taken effect', async () => {
      fetchMock.mockImplementation(async () => droppedBody())
      const result = await settle(
        makeStore().dispatch(api.endpoints.saveThing.initiate())
      )
      expect(result.error).toMatchObject({ status: 'PARSING_ERROR' })
      expect(fetchMock).toHaveBeenCalledTimes(1)
    })
  })

  describe('a response that is not JSON', () => {
    it.each([200, 502])(
      'is not retried when the status is %i',
      async (status) => {
        fetchMock.mockImplementation(
          async () => new Response('<html>Bad gateway</html>', { status })
        )
        const result = await settle(
          makeStore().dispatch(api.endpoints.getThing.initiate())
        )
        expect(result.error).toMatchObject({
          status: 'PARSING_ERROR',
          originalStatus: status,
        })
        expect(fetchMock).toHaveBeenCalledTimes(1)
      }
    )
  })
})
