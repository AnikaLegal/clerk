import { describe, expect, it } from 'vitest'

import { buildSurveyModel } from '../src/form/model'
import { navigableSections, readSectionStates } from '../src/form/section-nav'
import { Answers } from '../src/form/types'
import { QUESTIONS_BY_NAME } from '../src/questions'

// Real (answer-holding) questions on every page up to and including the cutoff
// - the shape `visited` has once the user has passed those pages.
const visitedThrough = (
  survey: ReturnType<typeof buildSurveyModel>,
  cutoffPage: string
): Set<string> => {
  const visited = new Set<string>()
  for (const page of survey.pages) {
    for (const el of page.questions) {
      const q = QUESTIONS_BY_NAME[el.name]
      if (q && q.type !== 'DISPLAY' && !q.uiOnly) visited.add(el.name)
    }
    if (page.name === cutoffPage) break
  }
  return visited
}

const setUp = (data: Answers, currentPage: string, cutoff = 'SUBMIT') => {
  const survey = buildSurveyModel()
  survey.data = data
  const page = survey.getPageByName(currentPage)
  if (!page) throw new Error(`no page ${currentPage}`)
  survey.currentPage = page
  return { survey, visited: visitedThrough(survey, cutoff) }
}

// A fully-answered repairs submission.
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

const keys = (m: Map<number, string>) => [...m.keys()].sort((a, b) => a - b)

describe('navigableSections', () => {
  it('offers every other section when the form is complete (jumped back)', () => {
    // Fully answered, then jumped back to an About-you page.
    const { survey, visited } = setUp(FULL, 'ABOUT_EMAIL')
    const nav = navigableSections(survey, visited)
    // 1 (Getting in touch) is current; 0 backward, 2-6 forward - all reachable,
    // including the final Submit step.
    expect(keys(nav)).toEqual([0, 2, 3, 4, 5, 6])
    // Each lands on the section's first visible page.
    expect(nav.get(0)).toBe('ELIGIBILITY_ISSUE')
    expect(nav.get(2)).toBe('REPAIRS_ABOUT')
    expect(nav.get(3)).toBe('PROPERTY_TENANCY')
    expect(nav.get(5)).toBe('IMPACT_ABOUT')
    expect(nav.get(6)).toBe('SUBMIT')
  })

  it('drops forward sections when an answer now triggers an exit', () => {
    // Non-Victorian tenant: the exit fires on this very page.
    const { survey, visited } = setUp(
      { ...FULL, IS_VICTORIAN_TENANT: false },
      'ELIGIBILITY_LOCATION'
    )
    // Can't pass the current page, and nothing precedes section 0 - so nothing.
    expect(keys(navigableSections(survey, visited))).toEqual([])
  })

  it('offers the forward sections again once the exit answer is cleared', () => {
    const { survey, visited } = setUp(FULL, 'ELIGIBILITY_LOCATION')
    // Getting started is current; Getting in touch through Submit are all
    // reachable.
    expect(keys(navigableSections(survey, visited))).toEqual([1, 2, 3, 4, 5, 6])
  })

  it('keeps the end locked when an exit sits ahead, even after stepping back behind it', () => {
    // At SUBMIT, jumped back to Getting started, chose the non-Victorian exit on
    // ELIGIBILITY_LOCATION, then stepped back to the page before it. The exit
    // now sits between the user and everything past it. The forward walk still
    // reaches the exit page and stops there, so nothing beyond it is offered -
    // the Submit step (the furthest page, section 6) least of all.
    const { survey, visited } = setUp(
      { ...FULL, IS_VICTORIAN_TENANT: false },
      'ELIGIBILITY_ISSUE'
    )
    const nav = navigableSections(survey, visited)
    expect(nav.has(6)).toBe(false)
    expect(keys(nav)).toEqual([])
  })

  it('offers reachable sections mid-form, including the next section start', () => {
    // Answered through Getting in touch, standing back on its first page,
    // nothing past it visited yet.
    const { survey, visited } = setUp(FULL, 'ABOUT_EMAIL', 'ABOUT_CONTACT')
    const nav = navigableSections(survey, visited)
    // Getting started is complete behind us, and Your problem's first page is
    // the next reachable page - so it is offered even though the section is not
    // yet started. Your home onward, past the unvisited Your problem pages, is
    // not.
    expect(keys(nav)).toEqual([0, 2])
    expect(nav.get(2)).toBe('REPAIRS_ABOUT')
  })

  it('omits a section whose whole branch is hidden', () => {
    // Bonds pages make up part of "Your problem"; on a repairs branch the
    // section still resolves to its repairs pages, never a bonds page.
    const { survey, visited } = setUp(FULL, 'ABOUT_EMAIL')
    expect(navigableSections(survey, visited).get(2)).toBe('REPAIRS_ABOUT')
  })
})

describe('readSectionStates', () => {
  const states = (data: Answers, currentPage: string, cutoff?: string) => {
    const { survey, visited } = setUp(data, currentPage, cutoff)
    return readSectionStates(survey, visited).map((s) => s.state)
  }

  it('keeps the answered sections done after a jump back into the form', () => {
    // Fully answered, then jumped back to an About-you page: the sections either
    // side stay complete, the one landed in reads as current, and Submit - which
    // holds no answers and has not been passed - is still ahead.
    expect(states(FULL, 'ABOUT_EMAIL')).toEqual([
      'done',
      'current',
      'done',
      'done',
      'done',
      'done',
      'later',
    ])
  })

  it('reports the current section complete when fully answered', () => {
    // The state stays `current`, but the completeness travels separately so the
    // marker keeps its tick when the user jumps back into a finished section.
    const { survey, visited } = setUp(FULL, 'ABOUT_EMAIL')
    expect(readSectionStates(survey, visited).map((s) => s.complete)).toEqual([
      true,
      true,
      true,
      true,
      true,
      true,
      false,
    ])
  })

  it('drops the ticks past an answer that now triggers an exit', () => {
    // Back on the first page of a complete form, having chosen the compensation
    // exit. Everything from that page on is unreachable, so no later section may
    // still read as complete - even though its answers are all there.
    expect(
      states(
        { ...FULL, ISSUES: 'INELIGIBLE_COMPENSATION' },
        'ELIGIBILITY_ISSUE'
      )
    ).toEqual(['current', 'later', 'later', 'later', 'later', 'later', 'later'])
  })

  it('drops the ticks past an exit the user has stepped back behind', () => {
    // The non-Victorian exit sits on ELIGIBILITY_LOCATION, one page ahead. The
    // section holding it is current, and nothing beyond the exit is complete.
    expect(
      states({ ...FULL, IS_VICTORIAN_TENANT: false }, 'ELIGIBILITY_ISSUE')
    ).toEqual(['current', 'later', 'later', 'later', 'later', 'later', 'later'])
  })

  it('marks only the passed sections done mid-form', () => {
    // Answered through Getting in touch, standing back on its first page: the
    // section behind is done, the rest are still ahead.
    expect(states(FULL, 'ABOUT_EMAIL', 'ABOUT_CONTACT')).toEqual([
      'done',
      'current',
      'later',
      'later',
      'later',
      'later',
      'later',
    ])
  })
})
