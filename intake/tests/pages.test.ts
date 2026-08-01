import { describe, expect, it } from 'vitest'

import { buildSurveyModel } from '../src/form/model'
import { PAGES, QUESTIONS, QUESTIONS_BY_NAME } from '../src/questions'

describe('page grouping', () => {
  it('places every question on exactly one page, in order', () => {
    const placed = PAGES.flatMap((page) => page.questions)

    // No question appears on more than one page.
    expect(new Set(placed).size).toBe(placed.length)
    // Every placed name is a real question.
    for (const name of placed) {
      expect(QUESTIONS_BY_NAME[name]).toBeDefined()
    }
    // Every question is placed on some page (and no extras).
    expect([...placed].sort()).toEqual(QUESTIONS.map((q) => q.name).sort())
    // Pages are consecutive chunks of the flat question order, so flattening
    // the pages reproduces the canonical question sequence exactly.
    expect(placed).toEqual(QUESTIONS.map((q) => q.name))
  })

  it('gives every page a unique name', () => {
    const names = PAGES.map((page) => page.name)
    expect(new Set(names).size).toBe(names.length)
  })

  it('clears a typed email when the no-email escape hatch is ticked', () => {
    const survey = buildSurveyModel()
    survey.setValue('EMAIL', 'typed@example.com')
    survey.setValue('NO_EMAIL', true)
    expect(survey.getValue('EMAIL')).toBeUndefined()
    // Unticking re-enables the field but doesn't resurrect the old value.
    survey.setValue('NO_EMAIL', false)
    expect(survey.getValue('EMAIL')).toBeUndefined()
  })

  it('keeps the home address block together on the address page', () => {
    const survey = buildSurveyModel()
    const page = survey.getPageByName('PROPERTY_ADDRESS')
    expect(page.questions.map((q) => q.name)).toEqual([
      'ADDRESS_INTRO',
      'ADDRESS_SEARCH',
      'ADDRESS_MANUAL',
      'ADDRESS',
      'SUBURB',
      'POSTCODE',
      'WEEKLY_RENT',
    ])
    // The fields hold flat top-level values (the backend wire contract).
    survey.setValue('ADDRESS', '12 Example Street')
    expect((survey.data as Record<string, unknown>).ADDRESS).toBe(
      '12 Example Street'
    )
  })
})
