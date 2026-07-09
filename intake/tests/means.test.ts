import { describe, expect, it } from 'vitest'

import { meansIneligible } from '../src/form/functions'

// Ported threshold matrix from the old form's ineligibleCriteria.
describe('meansIneligible', () => {
  it.each([
    // [centrelink, circumstances, income, dependants, expected]
    [true, undefined, 'OVER_155K', 0, false], // centrelink always passes
    [false, ['STRUGGLING'], 'OVER_155K', 0, false], // any circumstance passes
    [false, undefined, 'OVER_155K', 5, true],
    [false, undefined, 'OVER_155K', 6, false],
    [false, undefined, 'FROM_140K_TO_155K', 4, true],
    [false, undefined, 'FROM_140K_TO_155K', 5, false],
    [false, undefined, 'FROM_115K_TO_139K', 2, true],
    [false, undefined, 'FROM_115K_TO_139K', 3, false],
    [false, undefined, 'FROM_90K_TO_114K', 0, true],
    [false, undefined, 'FROM_90K_TO_114K', 1, false],
    [false, undefined, 'FROM_65K_TO_89K', 0, false], // low incomes always pass
    [false, undefined, 'FROM_40K_TO_64K', 0, false],
    [false, undefined, 'UNDER_40K', 0, false],
    [false, null, 'OVER_155K', 0, true], // null circumstances == skipped
    [false, [], 'OVER_155K', 0, true], // SurveyJS passes [] for unanswered checkboxes
  ])(
    'centrelink=%s circumstances=%s income=%s dependants=%s -> %s',
    (centrelink, circumstances, income, dependants, expected) => {
      expect(
        meansIneligible(centrelink, circumstances, income, dependants)
      ).toBe(expected)
    }
  )
})
