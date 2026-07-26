import { describe, expect, it } from 'vitest'

import { buildSurveyModel } from '../src/form/model'
import { PHONE_MAX_LENGTH, PHONE_VALIDATOR } from '../src/form/phone'

// These caps mirror the length of the DB column each answer is written to in
// core/services/submission.py, so a user can't enter data that overflows the
// field when the submission is processed. This test guards against the caps
// silently disappearing (a dropped maxLength or broken model wiring). It can
// only pin the cap values, not cross-check the live DB columns (those limits
// live in the Python models, out of reach here) - so if a column is ever
// resized, both sides must be kept in sync by hand.

// question name -> expected character cap (matches the DB column length)
const TEXT_CAPS: Record<string, number> = {
  FIRST_NAME: 150,
  LAST_NAME: 150,
  PREFERRED_NAME: 150,
  EMAIL: 150,
  SUBURB: 128,
  ADDRESS: 256,
  FIRST_LANGUAGE: 64,
  AGENT_NAME: 256,
  AGENT_ADDRESS: 256,
  AGENT_EMAIL: 150,
  LANDLORD_NAME: 256,
  LANDLORD_ADDRESS: 256,
  LANDLORD_EMAIL: 150,
}

// question name -> expected numeric max (fits its column, e.g. postcode's 6
// chars, weekly_rent's integer field)
const NUMBER_CAPS: Record<string, number> = {
  POSTCODE: 999999,
  WEEKLY_RENT: 100000,
}

describe('input length caps', () => {
  const survey = buildSurveyModel()

  it.each(Object.entries(TEXT_CAPS))(
    'caps %s at %i chars',
    (name, expected) => {
      expect(survey.getQuestionByName(name)?.maxLength).toBe(expected)
    }
  )

  it.each(Object.entries(NUMBER_CAPS))(
    'caps %s at a max value of %i',
    (name, expected) => {
      const validators = survey.getQuestionByName(name)?.validators ?? []
      const numeric = validators.find(
        (v) => (v as unknown as { maxValue?: number }).maxValue != null
      )
      expect((numeric as unknown as { maxValue?: number })?.maxValue).toBe(
        expected
      )
    }
  )

  // PHONE / AGENT_PHONE / LANDLORD_PHONE are not plain maxLength text fields:
  // the length cap and format validator are injected together in the model's
  // PHONE branch (model.ts). Pin that wiring - a dropped branch would let an
  // oversized number reach the 32 char phone column - including the
  // user-facing error message.
  it.each(['PHONE', 'AGENT_PHONE', 'LANDLORD_PHONE'])(
    'caps and format-validates %s',
    (name) => {
      const question = survey.getQuestionByName(name)
      expect(question?.maxLength).toBe(PHONE_MAX_LENGTH)
      const regex = (question?.validators ?? []).find(
        (v) =>
          (v as unknown as { regex?: string }).regex === PHONE_VALIDATOR.regex
      )
      expect(regex).toBeDefined()
      expect((regex as unknown as { text?: string }).text).toBe(
        PHONE_VALIDATOR.text
      )
    }
  )

  it('caps the gender self-describe text at 64 chars', () => {
    expect(survey.maxOthersLength).toBe(64)
  })
})
