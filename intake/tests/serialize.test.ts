import { describe, expect, it } from 'vitest'

import { buildSurveyModel } from '../src/form/model'
import { deserializeAnswers, serializeAnswers } from '../src/form/serialize'
import { NONE_OF_THE_ABOVE } from '../src/form/types'

const UPLOAD = { id: 'abc-123', issue: null, file: 'https://s3/photo.png' }

describe('serializeAnswers', () => {
  it('reproduces the old tidyData payload contract', () => {
    const survey = buildSurveyModel()
    survey.autoAdvanceEnabled = false
    survey.data = {
      ISSUES: 'REPAIRS',
      IS_VICTORIAN_TENANT: true,
      CENTRELINK_SUPPORT: true,
      NUMBER_OF_DEPENDENTS: 0,
      EMAIL: 'test@example.com',
      REPAIRS_ISSUE_PHOTO: [
        { name: 'photo.png', type: 'image/png', content: UPLOAD },
      ],
      WORK_OR_STUDY_CIRCUMSTANCES: NONE_OF_THE_ABOVE,
    }
    const visited = new Set([
      'ISSUES',
      'IS_VICTORIAN_TENANT',
      'CENTRELINK_SUPPORT',
      'NUMBER_OF_DEPENDENTS',
      'ELIGIBILITY_CIRCUMSTANCES', // visited but skipped
      'EMAIL',
      'REPAIRS_ISSUE_PHOTO',
      'WORK_OR_STUDY_CIRCUMSTANCES',
    ])
    const answers = serializeAnswers(survey, visited)

    // Visited answers present with their raw values.
    expect(answers.ISSUES).toBe('REPAIRS')
    expect(answers.IS_VICTORIAN_TENANT).toBe(true)
    expect(answers.NUMBER_OF_DEPENDENTS).toBe(0)
    // Visited but skipped -> null (not absent).
    expect(answers.ELIGIBILITY_CIRCUMSTANCES).toBeNull()
    // Upload values unwrap to the backend Upload objects.
    expect(answers.REPAIRS_ISSUE_PHOTO).toEqual([UPLOAD])
    // The null-choice sentinel maps back to null.
    expect(answers.WORK_OR_STUDY_CIRCUMSTANCES).toBeNull()
    // Never-visited questions are absent.
    expect('FIRST_NAME' in answers).toBe(false)
    // Question on a branch not taken (bonds while ISSUES=REPAIRS) is absent
    // even if it somehow had a stale value.
    expect('BOND_RTBA' in answers).toBe(false)
    // DISPLAY questions are never in the payload.
    expect('INTRO' in answers).toBe(false)
    expect('SUBMIT' in answers).toBe(false)
  })

  it('drops answers from branches no longer taken', () => {
    const survey = buildSurveyModel()
    survey.autoAdvanceEnabled = false
    // User answered bonds questions, then went back and switched to repairs.
    survey.data = {
      ISSUES: 'REPAIRS',
      BOND_RTBA: true,
    }
    const visited = new Set(['ISSUES', 'BOND_RTBA'])
    const answers = serializeAnswers(survey, visited)
    expect('BOND_RTBA' in answers).toBe(false)
  })
})

describe('deserializeAnswers', () => {
  it('round-trips a stored submission back into survey state', () => {
    const wire = {
      ISSUES: 'REPAIRS',
      IS_VICTORIAN_TENANT: true,
      ELIGIBILITY_CIRCUMSTANCES: null,
      REPAIRS_ISSUE_PHOTO: [UPLOAD],
      WORK_OR_STUDY_CIRCUMSTANCES: null,
    }
    const data = deserializeAnswers(wire)
    expect(data.ISSUES).toBe('REPAIRS')
    expect(data.IS_VICTORIAN_TENANT).toBe(true)
    // Nulls are dropped (SurveyJS represents "no answer" as absence)...
    expect('ELIGIBILITY_CIRCUMSTANCES' in data).toBe(false)
    // ...except null-choice questions, which map to the sentinel.
    expect(data.WORK_OR_STUDY_CIRCUMSTANCES).toBe(NONE_OF_THE_ABOVE)
    // Uploads regain the SurveyJS file item shape.
    expect(data.REPAIRS_ISSUE_PHOTO).toEqual([
      { name: 'photo.png', type: '', content: UPLOAD },
    ])
  })
})
