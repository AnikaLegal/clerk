import { describe, expect, it } from 'vitest'

import { ROUTES } from '../src/consts'
import { getExitRoute } from '../src/form/exits'

const DAY_MS = 24 * 60 * 60 * 1000
const dateString = (offsetDays: number) =>
  new Date(Date.now() + offsetDays * DAY_MS).toISOString().slice(0, 10)

describe('eligibility exits', () => {
  it('exits to compensation scope page', () => {
    expect(getExitRoute('ISSUES', { ISSUES: 'INELIGIBLE_COMPENSATION' })).toBe(
      ROUTES.LEGAL_SCOPE_COMPENSATION
    )
    expect(getExitRoute('ISSUES', { ISSUES: 'REPAIRS' })).toBeUndefined()
  })

  it('exits non-Victorian tenants', () => {
    expect(
      getExitRoute('IS_VICTORIAN_TENANT', { IS_VICTORIAN_TENANT: false })
    ).toBe(ROUTES.GEOGRAPHY)
    expect(
      getExitRoute('IS_VICTORIAN_TENANT', { IS_VICTORIAN_TENANT: true })
    ).toBeUndefined()
  })

  it('exits users who decline to continue after failing the means test', () => {
    expect(
      getExitRoute('INELIGIBLE_CHOICE', { INELIGIBLE_CHOICE: false })
    ).toBe(ROUTES.INELIGIBLE_MEANS)
    expect(
      getExitRoute('INELIGIBLE_CHOICE', { INELIGIBLE_CHOICE: true })
    ).toBeUndefined()
  })

  it('exits repairs users who already have a VCAT order', () => {
    expect(
      getExitRoute('REPAIRS_VCAT', { REPAIRS_VCAT: ['CAV', 'GOTTEN_VCAT'] })
    ).toBe(ROUTES.INELIGIBLE_REPAIRS_GOTTEN_VCAT)
    expect(
      getExitRoute('REPAIRS_VCAT', { REPAIRS_VCAT: ['APPLIED_VCAT'] })
    ).toBeUndefined()
  })

  it('exits repairs users at VCAT stage who decline to continue', () => {
    expect(
      getExitRoute('REPAIRS_APPLIED_VCAT', { REPAIRS_APPLIED_VCAT: false })
    ).toBe(ROUTES.INELIGIBLE_REPAIRS_APPLIED_VCAT)
  })

  it.each([
    ['BONDS_MOVE_OUT_DATE', null],
    ['BOND_RTBA', false],
    ['BONDS_LANDLORD_INTENTS_TO_MAKE_CLAIM', false],
    ['BONDS_HAS_LANDLORD_MADE_RTBA_APPLICATION', false],
    ['BONDS_HAS_LANDLORD_MADE_RTBA_APPLICATION', "I don't know"],
  ])('exits out-of-scope bonds cases (%s = %s)', (name, value) => {
    expect(getExitRoute(name, { [name]: value })).toBe(ROUTES.BONDS_RECOVERY)
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
    ).toBe(ROUTES.INELIGIBLE_ALREADY_REMOVED)
    expect(
      getExitRoute('EVICTION_RETALIATORY_HAS_NOTICE', {
        EVICTION_RETALIATORY_HAS_NOTICE: false,
      })
    ).toBe(ROUTES.INELIGIBLE_NO_EVICTIONS_NOTICE)
  })

  it('exits VCAT hearings within a fortnight, keeps later hearings', () => {
    expect(
      getExitRoute('EVICTION_RETALIATORY_VCAT_HEARING_DATE', {
        EVICTION_RETALIATORY_VCAT_HEARING_DATE: dateString(7),
      })
    ).toBe(ROUTES.INELIGIBLE_VCAT_HEARING)
    expect(
      getExitRoute('EVICTION_RETALIATORY_VCAT_HEARING_DATE', {
        EVICTION_RETALIATORY_VCAT_HEARING_DATE: dateString(30),
      })
    ).toBeUndefined()
  })
})
