import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { events } from '../src/analytics'

// The GA4 funnel depends on the exact event names and parameter keys, which
// nothing else would fail on if they drifted - so pin them here. The node test
// env has no window, so stub the gtag / fbq the analytics module calls.
const gtag = vi.fn()
const fbq = vi.fn()

beforeEach(() => {
  gtag.mockClear()
  fbq.mockClear()
  vi.stubGlobal('window', { gtag, fbq })
})

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('analytics events', () => {
  it('onFormBegin sends form_begin with the form id', () => {
    events.onFormBegin()
    expect(gtag).toHaveBeenCalledWith('event', 'form_begin', {
      form_id: 'intake',
    })
  })

  it('onFormComplete sends form_complete and the Facebook conversion', () => {
    events.onFormComplete()
    expect(gtag).toHaveBeenCalledWith('event', 'form_complete', {
      form_id: 'intake',
    })
    expect(fbq).toHaveBeenCalledWith('track', 'SubmitApplication')
  })

  it('onFormStep sends form_step with the funnel parameters', () => {
    events.onFormStep({ index: 3, name: 'ABOUT_EMAIL', section: 'About you' })
    expect(gtag).toHaveBeenCalledWith('event', 'form_step', {
      form_id: 'intake',
      step_index: 3,
      step_name: 'ABOUT_EMAIL',
      section: 'About you',
    })
  })

  it('onFormStep omits section when the page has none', () => {
    events.onFormStep({ index: 0, name: 'WELCOME' })
    expect(gtag).toHaveBeenCalledWith('event', 'form_step', {
      form_id: 'intake',
      step_index: 0,
      step_name: 'WELCOME',
    })
  })

  it('onFormExit sends form_exit with the trigger and destination', () => {
    events.onFormExit({
      question: 'BOND_RTBA',
      route: '/ineligible/bond-out-of-scope/',
    })
    expect(gtag).toHaveBeenCalledWith('event', 'form_exit', {
      form_id: 'intake',
      question: 'BOND_RTBA',
      route: '/ineligible/bond-out-of-scope/',
    })
  })
})
