import { describe, expect, it, vi } from 'vitest'

// The EMAIL side effect creates the submission; stub the network so it is a
// no-op we can assert on.
vi.mock('../src/api', () => ({
  api: {
    submission: {
      create: vi.fn().mockResolvedValue({ id: 'sub-1', answers: {} }),
      update: vi.fn(),
      submit: vi.fn(),
    },
  },
}))
vi.mock('../src/utils', () => ({ logException: vi.fn() }))

import { api } from '../src/api'
import { ROUTES } from '../src/consts'
import { buildSurveyModel } from '../src/form/model'
import { applyPageAdvance } from '../src/form/page-advance'
import { SubmissionSaver } from '../src/form/save'
import { Answers } from '../src/form/types'

const setUp = (data: Answers) => {
  const survey = buildSurveyModel()
  survey.autoAdvanceEnabled = false
  survey.data = data
  const saver = new SubmissionSaver(null, () => {})
  return { survey, saver }
}

const pageOf = (survey: ReturnType<typeof buildSurveyModel>, name: string) => {
  const page = survey.getPageByName(name)
  if (!page) throw new Error(`no page ${name}`)
  return page
}

describe('applyPageAdvance', () => {
  it('applies a skip default to a blank question and marks the page visited', () => {
    const { survey, saver } = setUp({})
    const visited = new Set<string>()
    const { answers, exit } = applyPageAdvance(
      survey,
      pageOf(survey, 'ELIGIBILITY_FINANCES'),
      visited,
      saver
    )
    // NUMBER_OF_DEPENDENTS was left blank, so its skipDefault (0) is applied.
    expect(answers.NUMBER_OF_DEPENDENTS).toBe(0)
    expect(visited.has('NUMBER_OF_DEPENDENTS')).toBe(true)
    // A DISPLAY block on the page never counts as an answered question.
    expect(visited.has('ELIGIBILITY_INTRO')).toBe(false)
    expect(exit).toBeNull()
  })

  it('leaves an answered question untouched by the skip default', () => {
    const { survey, saver } = setUp({ NUMBER_OF_DEPENDENTS: 3 })
    const { answers } = applyPageAdvance(
      survey,
      pageOf(survey, 'ELIGIBILITY_FINANCES'),
      new Set(),
      saver
    )
    expect(answers.NUMBER_OF_DEPENDENTS).toBe(3)
  })

  it('returns the exit route and triggering question when disqualified', () => {
    const { survey, saver } = setUp({ IS_VICTORIAN_TENANT: false })
    const visited = new Set<string>()
    const { exit } = applyPageAdvance(
      survey,
      pageOf(survey, 'ELIGIBILITY_LOCATION'),
      visited,
      saver
    )
    expect(exit).toEqual({
      route: ROUTES.INELIGIBLE_OUTSIDE_VICTORIA,
      question: 'IS_VICTORIAN_TENANT',
    })
    // The disqualifying question is still recorded as passed.
    expect(visited.has('IS_VICTORIAN_TENANT')).toBe(true)
  })

  it('returns no exit for an eligible answer', () => {
    const { survey, saver } = setUp({ IS_VICTORIAN_TENANT: true })
    const { exit } = applyPageAdvance(
      survey,
      pageOf(survey, 'ELIGIBILITY_LOCATION'),
      new Set(),
      saver
    )
    expect(exit).toBeNull()
  })

  it('runs a question side effect (creates the submission once email is given)', () => {
    const { survey, saver } = setUp({ EMAIL: 'test@example.com' })
    applyPageAdvance(survey, pageOf(survey, 'ABOUT_EMAIL'), new Set(), saver)
    expect(api.submission.create).toHaveBeenCalledTimes(1)
  })
})
