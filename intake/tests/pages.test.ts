import { describe, expect, it } from 'vitest'

import { buildSurveyModel } from '../src/form/model'
import { pageQuestionNames } from '../src/form/types'
import { PAGES, QUESTIONS, QUESTIONS_BY_NAME } from '../src/questions'

describe('page grouping', () => {
  it('places every question on exactly one page, in order', () => {
    const placed = PAGES.flatMap(pageQuestionNames)

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

  it('groups the home address block into a panel with flat values', () => {
    const survey = buildSurveyModel()
    const panel = survey.getPanelByName('HOME_ADDRESS')
    expect(panel).toBeTruthy()
    expect(panel.questions.map((q) => q.name)).toEqual([
      'ADDRESS_SEARCH',
      'ADDRESS_MANUAL',
      'ADDRESS',
      'SUBURB',
      'POSTCODE',
    ])
    // Panels are presentational only: the questions inside keep their own
    // flat top-level values (the backend wire contract).
    survey.setValue('ADDRESS', '12 Example Street')
    expect((survey.data as Record<string, unknown>).ADDRESS).toBe(
      '12 Example Street'
    )
  })
})
