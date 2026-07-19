import { describe, expect, it } from 'vitest'

import { buildSurveyModel } from '../src/form/model'

// Optional questions carry an "(optional)" suffix on their title (see
// form/model.ts titleFor) so users know they can skip them. Required
// questions keep SurveyJS's asterisk and no suffix; conditionally-required
// questions (requiredIf) are left unmarked because they are sometimes
// required.

describe('optional labels', () => {
  const survey = buildSurveyModel()
  const title = (name: string) => survey.getQuestionByName(name)?.title ?? ''

  it.each([
    'PREFERRED_NAME',
    'NUMBER_OF_DEPENDENTS',
    'AGENT_NAME',
    'AGENT_EMAIL',
    'LANDLORD_PHONE',
    'REPAIRS_ISSUE_PHOTO',
  ])('marks %s as optional', (name) => {
    expect(title(name)).toMatch(/\(optional\)$/)
  })

  it('leaves required questions unmarked', () => {
    expect(title('FIRST_NAME')).not.toContain('(optional)')
    expect(title('WEEKLY_RENT')).not.toContain('(optional)')
  })

  it('leaves conditionally-required questions unmarked', () => {
    // The address fields are required in manual mode (requiredIf), so calling
    // them optional would mislead.
    expect(title('ADDRESS_SEARCH')).not.toContain('(optional)')
    expect(title('ADDRESS')).not.toContain('(optional)')
    expect(title('SUBURB')).not.toContain('(optional)')
    expect(title('POSTCODE')).not.toContain('(optional)')
  })

  it('leaves the manual-entry checkbox label unmarked', () => {
    const checkbox = survey.getQuestionByName('ADDRESS_MANUAL') as unknown as {
      label: string
    }
    expect(checkbox.label).toBe('Enter address manually')
  })
})
