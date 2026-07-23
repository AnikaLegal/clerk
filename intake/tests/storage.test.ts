import { afterEach, describe, expect, it, vi } from 'vitest'

import { STORAGE_KEY } from '../src/consts'
import {
  StoredState,
  clearState,
  loadState,
  saveState,
} from '../src/form/storage'

const EMPTY: StoredState = {
  submissionId: null,
  data: {},
  visited: [],
  currentPage: null,
  session: null,
}

const STATE: StoredState = {
  submissionId: 'sub-1',
  data: { EMAIL: 'test@example.com', ISSUES: ['REPAIRS'] },
  visited: ['EMAIL', 'ISSUES'],
  currentPage: 'ISSUES_REPAIRS',
  session: 'session-abc',
}

// The tests run in node, so provide a minimal Map-backed localStorage. The
// throwing variant simulates private browsing / storage denied / quota full.
const stubStorage = () => {
  const store = new Map<string, string>()
  vi.stubGlobal('localStorage', {
    getItem: (key: string) => store.get(key) ?? null,
    setItem: (key: string, value: string) => void store.set(key, value),
    removeItem: (key: string) => void store.delete(key),
  })
  return store
}

const stubBrokenStorage = () => {
  const denied = () => {
    throw new Error('storage denied')
  }
  vi.stubGlobal('localStorage', {
    getItem: denied,
    setItem: denied,
    removeItem: denied,
  })
}

describe('storage', () => {
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('round-trips state through localStorage', () => {
    stubStorage()
    saveState(STATE)
    expect(loadState()).toEqual(STATE)
  })

  it('returns empty state when nothing is stored', () => {
    stubStorage()
    expect(loadState()).toEqual(EMPTY)
  })

  it('returns an independent state object on every load', () => {
    stubStorage()
    const first = loadState()
    first.visited.push('EMAIL')
    first.data.EMAIL = 'mutated@example.com'
    expect(loadState()).toEqual(EMPTY)
  })

  it('clears stored state', () => {
    stubStorage()
    saveState(STATE)
    clearState()
    expect(loadState()).toEqual(EMPTY)
  })

  it.each(['not json at all', '"a string"', '42', 'null'])(
    'tolerates corrupt stored JSON: %s',
    (raw) => {
      const store = stubStorage()
      store.set(STORAGE_KEY, raw)
      expect(loadState()).toEqual(EMPTY)
    }
  )

  it('repairs wrong-shaped fields to safe defaults', () => {
    const store = stubStorage()
    store.set(
      STORAGE_KEY,
      JSON.stringify({ submissionId: 'sub-9', data: null, visited: 'EMAIL' })
    )
    expect(loadState()).toEqual({ ...EMPTY, submissionId: 'sub-9' })
  })

  it('survives an unavailable localStorage', () => {
    stubBrokenStorage()
    expect(loadState()).toEqual(EMPTY)
    expect(() => saveState(STATE)).not.toThrow()
    expect(() => clearState()).not.toThrow()
  })
})
