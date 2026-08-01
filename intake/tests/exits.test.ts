import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { ROUTES } from '../src/consts'
import { getExitRoute } from '../src/form/exits'

const DAY_MS = 24 * 60 * 60 * 1000
const dateString = (offsetDays: number) =>
  new Date(Date.now() + offsetDays * DAY_MS).toISOString().slice(0, 10)

const HEARING = 'EVICTION_RETALIATORY_VCAT_HEARING_DATE'
const hearingExit = (value: string) =>
  getExitRoute(HEARING, { [HEARING]: value })

describe('eligibility exits', () => {
  it('exits users without an email to the contact fallback', () => {
    expect(getExitRoute('NO_EMAIL', { NO_EMAIL: true })).toBe(ROUTES.NO_EMAIL)
    expect(getExitRoute('NO_EMAIL', { NO_EMAIL: false })).toBeUndefined()
    expect(getExitRoute('NO_EMAIL', {})).toBeUndefined()
  })

  it('exits to compensation scope page', () => {
    expect(getExitRoute('ISSUES', { ISSUES: 'INELIGIBLE_COMPENSATION' })).toBe(
      ROUTES.INELIGIBLE_COMPENSATION
    )
    expect(getExitRoute('ISSUES', { ISSUES: 'REPAIRS' })).toBeUndefined()
  })

  it('exits non-Victorian tenants', () => {
    expect(
      getExitRoute('IS_VICTORIAN_TENANT', { IS_VICTORIAN_TENANT: false })
    ).toBe(ROUTES.INELIGIBLE_OUTSIDE_VICTORIA)
    expect(
      getExitRoute('IS_VICTORIAN_TENANT', { IS_VICTORIAN_TENANT: true })
    ).toBeUndefined()
  })

  it('exits users who decline to continue after failing the means test', () => {
    expect(
      getExitRoute('INELIGIBLE_CHOICE', { INELIGIBLE_CHOICE: false })
    ).toBe(ROUTES.INELIGIBLE_INCOME)
    expect(
      getExitRoute('INELIGIBLE_CHOICE', { INELIGIBLE_CHOICE: true })
    ).toBeUndefined()
  })

  it('exits repairs users who already have a VCAT order', () => {
    expect(
      getExitRoute('REPAIRS_VCAT', { REPAIRS_VCAT: ['CAV', 'GOTTEN_VCAT'] })
    ).toBe(ROUTES.INELIGIBLE_REPAIRS_ORDER_OBTAINED)
    expect(
      getExitRoute('REPAIRS_VCAT', { REPAIRS_VCAT: ['APPLIED_VCAT'] })
    ).toBeUndefined()
  })

  it('exits repairs users at VCAT stage who decline to continue', () => {
    expect(
      getExitRoute('REPAIRS_APPLIED_VCAT', { REPAIRS_APPLIED_VCAT: false })
    ).toBe(ROUTES.EXIT_VCAT_REPRESENTATION)
  })

  it.each([
    ['BONDS_MOVE_OUT_DATE', null],
    ['BOND_RTBA', false],
    ['BONDS_HAS_LANDLORD_MADE_RTBA_APPLICATION', false],
    ['BONDS_HAS_LANDLORD_MADE_RTBA_APPLICATION', "I don't know"],
  ])('exits out-of-scope bonds cases (%s = %s)', (name, value) => {
    expect(getExitRoute(name, { [name]: value })).toBe(
      ROUTES.INELIGIBLE_BOND_OUT_OF_SCOPE
    )
  })

  it('keeps in-scope bonds cases', () => {
    expect(
      getExitRoute('BONDS_MOVE_OUT_DATE', { BONDS_MOVE_OUT_DATE: '2026-01-01' })
    ).toBeUndefined()
    expect(
      getExitRoute('BONDS_HAS_LANDLORD_MADE_RTBA_APPLICATION', {
        BONDS_HAS_LANDLORD_MADE_RTBA_APPLICATION: true,
      })
    ).toBeUndefined()
  })

  it('exits evicted users and users without a notice', () => {
    expect(
      getExitRoute('EVICTION_RETALIATORY_IS_ALREADY_REMOVED', {
        EVICTION_RETALIATORY_IS_ALREADY_REMOVED: true,
      })
    ).toBe(ROUTES.INELIGIBLE_ALREADY_EVICTED)
    expect(
      getExitRoute('EVICTION_RETALIATORY_HAS_NOTICE', {
        EVICTION_RETALIATORY_HAS_NOTICE: false,
      })
    ).toBe(ROUTES.INELIGIBLE_NO_NOTICE_TO_VACATE)
  })

  it('exits VCAT hearings within a fortnight, keeps later hearings', () => {
    expect(hearingExit(dateString(7))).toBe(ROUTES.INELIGIBLE_URGENT_HEARING)
    expect(hearingExit(dateString(30))).toBeUndefined()
  })
})

describe('VCAT hearing fortnight boundary', () => {
  beforeEach(() => vi.useFakeTimers())
  afterEach(() => vi.useRealTimers())

  it('exits a hearing exactly 14 calendar days away, regardless of time of day', () => {
    // Late in the local day: the old UTC-parse vs local-now comparison flipped
    // an exactly-14-days hearing between eligible (morning) and ineligible
    // (afternoon). Calendar-day math must not.
    vi.setSystemTime(new Date(2026, 0, 1, 23, 30, 0))
    expect(hearingExit('2026-01-15')).toBe(ROUTES.INELIGIBLE_URGENT_HEARING)
    vi.setSystemTime(new Date(2026, 0, 1, 0, 30, 0))
    expect(hearingExit('2026-01-15')).toBe(ROUTES.INELIGIBLE_URGENT_HEARING)
  })

  it('keeps a hearing 15 days away', () => {
    vi.setSystemTime(new Date(2026, 0, 1, 9, 0, 0))
    expect(hearingExit('2026-01-16')).toBeUndefined()
  })

  it('exits a hearing today and one on the fortnight boundary', () => {
    vi.setSystemTime(new Date(2026, 0, 1, 12, 0, 0))
    expect(hearingExit('2026-01-01')).toBe(ROUTES.INELIGIBLE_URGENT_HEARING)
    expect(hearingExit('2026-01-14')).toBe(ROUTES.INELIGIBLE_URGENT_HEARING)
  })

  it('treats a missing or unparseable date as no exit (fail-open)', () => {
    vi.setSystemTime(new Date(2026, 0, 1, 12, 0, 0))
    expect(hearingExit('')).toBeUndefined()
    expect(hearingExit('not-a-date')).toBeUndefined()
    expect(hearingExit('2026-02-31')).toBeUndefined()
    expect(getExitRoute(HEARING, {})).toBeUndefined()
  })
})
