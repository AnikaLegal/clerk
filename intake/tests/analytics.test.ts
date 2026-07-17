import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { events } from '../src/analytics'

// The GA4 funnel depends on the exact event name and parameter keys, which
// nothing else would fail on if they drifted - so pin them here. The node test
// env has no window, so stub the gtag the analytics module calls.
const gtag = vi.fn()

beforeEach(() => {
  gtag.mockClear()
  vi.stubGlobal('window', { gtag, fbq: vi.fn() })
})

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('analytics onFormStep', () => {
  it('sends form_step with the funnel parameters', () => {
    events.onFormStep({ index: 3, name: 'ABOUT_EMAIL', section: 'About you' })
    expect(gtag).toHaveBeenCalledWith('event', 'form_step', {
      form_id: 'intake',
      step_index: 3,
      step_name: 'ABOUT_EMAIL',
      section: 'About you',
    })
  })

  it('omits section when the page has none', () => {
    events.onFormStep({ index: 0, name: 'WELCOME' })
    expect(gtag).toHaveBeenCalledWith('event', 'form_step', {
      form_id: 'intake',
      step_index: 0,
      step_name: 'WELCOME',
    })
  })
})
