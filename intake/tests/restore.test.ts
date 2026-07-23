import { describe, expect, it } from 'vitest'

import { buildSurveyModel, WELCOME_PAGE } from '../src/form/model'
import { restorePosition } from '../src/form/restore'
import { QUESTIONS_BY_NAME } from '../src/questions'

// Every real (answer-holding) question on the visible pages up to and
// including the cutoff - the shape a server resume's visited set has, since it
// is seeded from the wire answer keys (which exclude DISPLAY and uiOnly).
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

const pageIndex = (survey: ReturnType<typeof buildSurveyModel>, name: string) =>
  survey.visiblePages.findIndex((p) => p.name === name)

describe('restorePosition', () => {
  it('restores the stored page when it is still visible', () => {
    const survey = buildSurveyModel()
    survey.data = { ISSUES: 'REPAIRS' }
    restorePosition(survey, new Set(['ISSUES']), 'ABOUT_NAME')
    expect(survey.currentPage.name).toBe('ABOUT_NAME')
  })

  it('skips a stored page on a branch no longer taken', () => {
    const survey = buildSurveyModel()
    // Answered as repairs, so a bonds-only page is not visible.
    survey.data = { ISSUES: 'REPAIRS' }
    restorePosition(survey, new Set(['ISSUES']), 'BONDS_BOND')
    expect(survey.currentPage.name).not.toBe('BONDS_BOND')
    expect(survey.currentPage.isVisible).toBe(true)
  })

  it('resumes past the address page when only the uiOnly parts are unvisited', () => {
    const survey = buildSurveyModel()
    // Maps available, so the (uiOnly) search box and manual checkbox are
    // visible - the case where the uiOnly exclusion actually matters.
    survey.data = { ISSUES: 'REPAIRS', MAPS_AVAILABLE: true }
    // Server-resume shape: every real question through the address page is
    // visited, but ADDRESS_SEARCH / ADDRESS_MANUAL (uiOnly) never are.
    const visited = visitedThrough(survey, 'PROPERTY_ADDRESS')
    restorePosition(survey, visited, null)
    expect(survey.currentPage.name).not.toBe('PROPERTY_ADDRESS')
    expect(pageIndex(survey, survey.currentPage.name)).toBeGreaterThan(
      pageIndex(survey, 'PROPERTY_ADDRESS')
    )
  })

  it('leaves a fresh visitor on the welcome page', () => {
    const survey = buildSurveyModel()
    restorePosition(survey, new Set(), null)
    expect(survey.currentPage.name).toBe(WELCOME_PAGE)
  })
})
