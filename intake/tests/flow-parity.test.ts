import { describe, expect, it } from 'vitest'

import { buildSurveyModel } from '../src/form/model'
import { Answers } from '../src/form/types'

/**
 * Walk the survey page by page, answering from the persona's answer map,
 * and return the sequence of visible question names encountered (in display
 * order). Pages now hold several questions, so every question the persona
 * answers is set before recording the page's visible questions - this lets
 * intra-page conditional questions resolve. Auto-advance is disabled so the
 * walk is deterministic.
 */
const walk = (answers: Answers): string[] => {
  const survey = buildSurveyModel()
  survey.autoAdvanceEnabled = false
  // Advance past the leading WELCOME page (intro only, no answers) so the walk
  // begins on the first real question page.
  survey.nextPage()
  const seen: string[] = []
  let guard = 0
  while (guard++ < 200) {
    const page = survey.currentPage
    if (!page) break
    // Set every answer the persona has for this page's questions first, so
    // conditional questions on the same page become visible.
    for (const el of page.elements) {
      const value = answers[el.name]
      if (value !== undefined && value !== null) {
        survey.setValue(el.name, value)
      }
    }
    for (const el of page.elements) {
      if (el.isVisible) seen.push(el.name)
    }
    if (survey.isLastPage) break
    const before = survey.currentPage.name
    survey.nextPage()
    if (survey.currentPage.name === before) {
      throw new Error(`Walk stuck on page ${before} (missing required answer?)`)
    }
  }
  return seen
}

const BASE_ANSWERS: Answers = {
  IS_VICTORIAN_TENANT: true,
  CENTRELINK_SUPPORT: true,
  NUMBER_OF_DEPENDENTS: 0,
  ELIGIBILITY_CIRCUMSTANCES: ['STRUGGLING'],
  EMAIL: 'test@example.com',
  FIRST_NAME: 'Jane',
  LAST_NAME: 'Doe',
  PREFERRED_NAME: 'Jane',
  PHONE: '0412345678',
  AVAILABILITY: ['WEEK_DAY'],
  RENTAL_CIRCUMSTANCES: 'SOLO',
  IS_ON_LEASE: 'YES',
  START_DATE: '2024-01-01',
  SUBURB: 'Fitzroy',
  POSTCODE: 3065,
  ADDRESS: '1 Test St',
  WEEKLY_RENT: 500,
  PROPERTY_MANAGER_IS_AGENT: true,
  AGENT_NAME: 'Agent',
  AGENT_ADDRESS: '2 Agent St',
  AGENT_EMAIL: 'agent@example.com',
  AGENT_PHONE: '0412000000',
  LANDLORD_NAME: 'Lorde Land',
  DOB: '1990-01-01',
  GENDER: 'FEMALE',
  IS_ABORIGINAL_OR_TORRES_STRAIT_ISLANDER: 'NO',
  CAN_SPEAK_NON_ENGLISH: false,
  WORK_OR_STUDY_CIRCUMSTANCES: 'WORKING_FULL_TIME',
  REFERRER_TYPE: 'SOCIAL_MEDIA',
  SOCIAL_REFERRER: 'Facebook',
}

describe('flow parity', () => {
  it('walks the full repairs flow in order', () => {
    const seen = walk({
      ...BASE_ANSWERS,
      ISSUES: 'REPAIRS',
      REPAIRS_ISSUE_START: '2025-01-01',
      REPAIRS_VCAT: ['Landlord'],
    })
    expect(seen).toEqual([
      'INTRO',
      'ISSUES',
      'IS_VICTORIAN_TENANT',
      'ELIGIBILITY_INTRO',
      'CENTRELINK_SUPPORT',
      'NUMBER_OF_DEPENDENTS',
      'ELIGIBILITY_CIRCUMSTANCES',
      'EMAIL',
      'FIRST_NAME',
      'LAST_NAME',
      'PREFERRED_NAME',
      'PHONE',
      'AVAILABILITY',
      'REPAIRS_INTRO',
      'REPAIRS_ISSUE_PHOTO',
      'REPAIRS_ISSUE_START',
      'REPAIRS_VCAT',
      'PROPERTY_INTRO',
      'RENTAL_CIRCUMSTANCES',
      'IS_ON_LEASE',
      'START_DATE',
      'ADDRESS',
      'SUBURB',
      'POSTCODE',
      'WEEKLY_RENT',
      'PROPERTY_MANAGER_INTRO',
      'PROPERTY_MANAGER_IS_AGENT',
      'AGENT_NAME',
      'AGENT_ADDRESS',
      'AGENT_EMAIL',
      'AGENT_PHONE',
      'LANDLORD_NAME',
      'IMPACT_INTRO',
      'DOB',
      'GENDER',
      'IS_ABORIGINAL_OR_TORRES_STRAIT_ISLANDER',
      'CAN_SPEAK_NON_ENGLISH',
      'WORK_OR_STUDY_CIRCUMSTANCES',
      'REFERRER_TYPE',
      'SOCIAL_REFERRER',
      'SUBMIT',
    ])
  })

  it('shows the applied-VCAT question when the user applied to VCAT', () => {
    const seen = walk({
      ...BASE_ANSWERS,
      ISSUES: 'REPAIRS',
      REPAIRS_ISSUE_START: '2025-01-01',
      REPAIRS_VCAT: ['APPLIED_VCAT'],
      REPAIRS_APPLIED_VCAT: true,
    })
    expect(seen).toContain('REPAIRS_APPLIED_VCAT')
  })

  it('walks every bonds sub-branch when all claim reasons are selected', () => {
    const seen = walk({
      ...BASE_ANSWERS,
      ISSUES: 'BONDS',
      BONDS_MOVE_OUT_DATE: '2026-01-01',
      BOND_RTBA: true,
      BONDS_LANDLORD_INTENTS_TO_MAKE_CLAIM: true,
      BONDS_HAS_LANDLORD_MADE_RTBA_APPLICATION: true,
      BONDS_TENANT_HAS_RTBA_APPLICATION_COPY: true,
      BONDS_CLAIM_REASONS: [
        'Damage',
        'Rent or other money owing',
        'Cleaning',
        'Locks and security devices',
        'Other reason',
      ],
      BONDS_DAMAGE_CLAIM_DESCRIPTION: 'Broken window',
      BONDS_DAMAGE_CLAIM_AMOUNT: 500,
      BONDS_DAMAGE_CAUSED_BY_TENANT: true,
      BONDS_MONEY_OWED_CLAIM_DESCRIPTION: 'Rent arrears',
      BONDS_MONEY_OWED_CLAIM_AMOUNT: 1000,
      BONDS_MONEY_IS_OWED_BY_TENANT: true,
      BONDS_CLEANING_CLAIM_DESCRIPTION: 'Carpet',
      BONDS_CLEANING_CLAIM_AMOUNT: 200,
      BONDS_LOCKS_CLAIM_AMOUNT: 100,
      BONDS_LOCKS_CHANGED_BY_TENANT: true,
      BONDS_OTHER_REASONS_DESCRIPTION: 'Misc',
      BONDS_OTHER_REASONS_AMOUNT: 50,
    })
    for (const name of [
      'BONDS_INTRO',
      'BONDS_DAMAGE_INTRO',
      'BONDS_DAMAGE_QUOTE_UPLOAD',
      'BONDS_MONEY_OWED_INTRO',
      'BONDS_CLEANING_INTRO',
      'BONDS_LOCKS_INTRO',
      'BONDS_LOCKS_CHANGE_QUOTE',
      'BONDS_OTHER_INTRO',
      'BONDS_RTBA_APPLICATION_UPLOAD',
    ]) {
      expect(seen).toContain(name)
    }
    // No other topic's questions leak into the bonds flow.
    expect(seen.some((name) => name.startsWith('REPAIRS_'))).toBe(false)
    expect(seen.some((name) => name.startsWith('EVICTION_'))).toBe(false)
  })

  it('walks the eviction flow including the pre-notice warning', () => {
    const seen = walk({
      ...BASE_ANSWERS,
      ISSUES: 'EVICTION_RETALIATORY',
      EVICTION_RETALIATORY_IS_ALREADY_REMOVED: false,
      EVICTION_RETALIATORY_HAS_NOTICE: true,
      EVICTION_RETALIATORY_DOCUMENTS_UPLOAD: [
        {
          name: 'ntv.pdf',
          type: '',
          content: { id: '1', issue: null, file: 'x' },
        },
      ] as unknown as Answers['EVICTION_RETALIATORY_DOCUMENTS_UPLOAD'],
      EVICTION_RETALIATORY_DATE_RECEIVED_NTV: '2025-06-01',
      EVICTION_RETALIATORY_NTV_TYPE: '91ZM - Arrears',
      EVICTION_RETALIATORY_RETALIATORY_REASON: ['Repairs'],
      EVICTION_RETALIATORY_VCAT_HEARING: false,
      EVICTION_RETALIATORY_TERMINATION_DATE: '2026-12-01',
    })
    expect(seen).toContain('PRE_EVICTION_NOTICE')
    expect(seen).toContain('EVICTION_RETALIATORY_NTV_TYPE')
    // No hearing date question when there is no hearing.
    expect(seen).not.toContain('EVICTION_RETALIATORY_VCAT_HEARING_DATE')
    expect(seen.some((name) => name.startsWith('BONDS_'))).toBe(false)
  })

  it('asks income and the means-test choice for high-income non-Centrelink users', () => {
    const answers: Answers = {
      ...BASE_ANSWERS,
      ISSUES: 'REPAIRS',
      CENTRELINK_SUPPORT: false,
      ANNUAL_INCOME_RANGE: 'OVER_155K',
      NUMBER_OF_DEPENDENTS: 0,
      INELIGIBLE_CHOICE: true,
      ELIGIBILITY_NOTES: 'Special circumstances',
      REPAIRS_ISSUE_START: '2025-01-01',
      REPAIRS_VCAT: ['Landlord'],
    }
    // The user skips the circumstances question.
    delete answers.ELIGIBILITY_CIRCUMSTANCES
    const seen = walk(answers)
    expect(seen).toContain('ANNUAL_INCOME_RANGE')
    expect(seen).toContain('INELIGIBLE_CHOICE')
    expect(seen).toContain('ELIGIBILITY_NOTES')
  })

  it('hides income questions for Centrelink recipients', () => {
    const seen = walk({
      ...BASE_ANSWERS,
      ISSUES: 'REPAIRS',
      REPAIRS_ISSUE_START: '2025-01-01',
      REPAIRS_VCAT: ['Landlord'],
    })
    expect(seen).not.toContain('ANNUAL_INCOME_RANGE')
    expect(seen).not.toContain('INELIGIBLE_CHOICE')
  })

  it('asks landlord contact details when there is no agent', () => {
    const seen = walk({
      ...BASE_ANSWERS,
      ISSUES: 'REPAIRS',
      REPAIRS_ISSUE_START: '2025-01-01',
      REPAIRS_VCAT: ['Landlord'],
      PROPERTY_MANAGER_IS_AGENT: false,
      LANDLORD_ADDRESS: '3 Owner St',
      LANDLORD_EMAIL: 'landlord@example.com',
      LANDLORD_PHONE: '0412999999',
    })
    expect(seen).not.toContain('AGENT_NAME')
    expect(seen).toContain('LANDLORD_NAME')
    expect(seen).toContain('LANDLORD_ADDRESS')
    expect(seen).toContain('LANDLORD_EMAIL')
    expect(seen).toContain('LANDLORD_PHONE')
  })

  it('asks interpreter questions for non-English speakers', () => {
    const seen = walk({
      ...BASE_ANSWERS,
      ISSUES: 'REPAIRS',
      REPAIRS_ISSUE_START: '2025-01-01',
      REPAIRS_VCAT: ['Landlord'],
      CAN_SPEAK_NON_ENGLISH: true,
      INTERPRETER: 'YES_SPOKEN',
      FIRST_LANGUAGE: 'Vietnamese',
    })
    expect(seen).toContain('INTERPRETER')
    expect(seen).toContain('FIRST_LANGUAGE')
  })
})
