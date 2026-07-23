import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import {
  markFormBegun,
  markStepReported,
  resetFunnel,
} from '../src/form/funnel'

// The tests run in node: back sessionStorage with a Map.
const stubStorage = () => {
  const store = new Map<string, string>()
  vi.stubGlobal('sessionStorage', {
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
  vi.stubGlobal('sessionStorage', {
    getItem: denied,
    setItem: denied,
    removeItem: denied,
  })
}

describe('funnel dedupe', () => {
  beforeEach(() => {
    stubStorage()
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('reports each step once, across notional remounts', () => {
    expect(markStepReported('ABOUT_EMAIL')).toBe(true)
    expect(markStepReported('ABOUT_EMAIL')).toBe(false)
    // A different page is still counted.
    expect(markStepReported('PROPERTY_ADDRESS')).toBe(true)
    // And the first page stays deduped.
    expect(markStepReported('ABOUT_EMAIL')).toBe(false)
  })

  it('reports form begin only once', () => {
    expect(markFormBegun()).toBe(true)
    expect(markFormBegun()).toBe(false)
  })

  it('begin and steps are tracked independently', () => {
    markStepReported('WELCOME')
    expect(markFormBegun()).toBe(true)
    expect(markStepReported('WELCOME')).toBe(false)
  })

  it('resetFunnel lets events fire again (fresh form in the same tab)', () => {
    markFormBegun()
    markStepReported('ABOUT_EMAIL')
    resetFunnel()
    expect(markFormBegun()).toBe(true)
    expect(markStepReported('ABOUT_EMAIL')).toBe(true)
  })

  it('falls back to firing (returns true) when storage is unavailable', () => {
    stubBrokenStorage()
    expect(markStepReported('ABOUT_EMAIL')).toBe(true)
    expect(markFormBegun()).toBe(true)
    expect(() => resetFunnel()).not.toThrow()
  })
})
