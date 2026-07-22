import { describe, expect, it } from 'vitest'

import { PHONE_VALIDATOR } from '../src/form/phone'

// The SurveyJS regex validator only runs on non-empty values (requiredness is
// a separate check), so these tests cover non-empty inputs only.
const isValidPhone = (value: string): boolean =>
  new RegExp(PHONE_VALIDATOR.regex).test(value)

describe('phone validation', () => {
  it.each([
    '0412345678',
    '+61412345678',
    '91234567', // Landline without an area code.
    '0391234567',
  ])('accepts %s', (value) => {
    expect(isValidPhone(value)).toBe(true)
  })

  it.each([
    'call me after 5pm', // Letters.
    'matt@foo.com',
    '0412345678x',
    '0412 345 678', // Separators are rejected: digits only.
    '(03) 9123 4567',
    '03-9123-4567',
    '1234', // Too few digits.
    '0412345678901234', // Too many digits.
    '+', // No digits at all.
    '0412+345678', // + is only allowed at the start.
  ])('rejects %s', (value) => {
    expect(isValidPhone(value)).toBe(false)
  })
})
