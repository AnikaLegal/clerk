import { describe, expect, it } from 'vitest'

import { buildSurveyModel } from '../src/form/model'
import { buildAnswerSummary } from '../src/form/review'
import { firstVisiblePageOfSection } from '../src/form/section-nav'
import { Answers } from '../src/form/types'

// A fully-answered repairs submission (mirrors the section-nav fixture).
const FULL: Answers = {
  ISSUES: 'REPAIRS',
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
  REPAIRS_ISSUE_START: '2025-01-01',
  REPAIRS_VCAT: ['Landlord'],
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

const setUp = (data: Answers) => {
  const survey = buildSurveyModel()
  survey.data = data
  return survey
}

describe('buildAnswerSummary', () => {
  it('groups answered questions by section with readable labels and values', () => {
    const summary = buildAnswerSummary(setUp(FULL))
    const byLabel = Object.fromEntries(summary.map((s) => [s.label, s]))

    const gettingStarted = byLabel['Getting started']
    expect(gettingStarted).toBeDefined()
    const rows = Object.fromEntries(
      gettingStarted.rows.map((r) => [
        r.name,
        { label: r.label, value: r.value },
      ])
    )
    // Choice values render as their labels, not the raw wire value.
    expect(rows.ISSUES).toEqual({
      label: 'What do you need help with?',
      value: "My landlord won't fix repairs",
    })
    // A boolean (yes/no) choice renders its label too.
    expect(rows.IS_VICTORIAN_TENANT.value).toBe('Yes')
  })

  it('renders labels as plain text, resolving placeholders and stripping markup', () => {
    const rowByName = Object.fromEntries(
      buildAnswerSummary(setUp(FULL))
        .flatMap((s) => s.rows)
        .map((r) => [r.name, r])
    )
    // Inline <strong> markup in the title is stripped.
    expect(rowByName.EMAIL.label).toBe("What's the best email to reach you?")
    // A {RENT_IS} placeholder is interpolated (repairs -> "is").
    expect(rowByName.WEEKLY_RENT.label).toBe('How much is your weekly rent?')
  })

  it('omits DISPLAY, uiOnly, unanswered and off-branch questions', () => {
    const names = buildAnswerSummary(setUp(FULL)).flatMap((s) =>
      s.rows.map((r) => r.name)
    )
    expect(names).not.toContain('SUBMIT') // DISPLAY (agreement page)
    expect(names).not.toContain('ADDRESS_SEARCH') // uiOnly
    expect(names).not.toContain('ADDRESS_MANUAL') // uiOnly
    // A bonds/eviction question is on a branch the repairs user isn't taking.
    expect(names).not.toContain('EVICTION_RETALIATORY_HAS_NOTICE')
    // Flat address fields inside the panel are still included.
    expect(names).toContain('ADDRESS')
    expect(names).toContain('POSTCODE')
  })

  it('drops sections with no answered questions', () => {
    // Only the opening eligibility answers; everything after is blank.
    const labels = buildAnswerSummary(
      setUp({ ISSUES: 'REPAIRS', IS_VICTORIAN_TENANT: true })
    ).map((s) => s.label)
    expect(labels).toEqual(['Getting started'])
  })
})

describe('firstVisiblePageOfSection', () => {
  it('returns the first visible page of a section', () => {
    const survey = setUp(FULL)
    expect(firstVisiblePageOfSection(survey, 0)).toBe('ELIGIBILITY_ISSUE')
    expect(firstVisiblePageOfSection(survey, 5)).toBe('IMPACT_ABOUT')
    // The final Submit section is the agreement page itself.
    expect(firstVisiblePageOfSection(survey, 6)).toBe('SUBMIT')
  })

  it('skips pages on a branch the user is not taking', () => {
    // Repairs branch: "Your problem" resolves to the repairs page, not a bond.
    expect(firstVisiblePageOfSection(setUp(FULL), 2)).toBe('REPAIRS_ABOUT')
  })
})
