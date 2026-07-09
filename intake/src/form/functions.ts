import { FunctionFactory } from 'survey-core'

// Means test, ported verbatim from the old intake repo's eligibility.js
// ineligibleCriteria. A user has failed the test when they receive no
// Centrelink support, skipped the eligibility circumstances question, and
// their household income is too high for their number of dependants.
export const meansIneligible = (
  centrelinkSupport: unknown,
  eligibilityCircumstances: unknown,
  annualIncomeRange: unknown,
  numberOfDependents: unknown
): boolean => {
  const dependants = Number(numberOfDependents ?? 0)
  // Skipped means unanswered: SurveyJS passes null/undefined for unanswered
  // questions in expressions, but an empty array for unanswered checkboxes
  // (the old form stored null on skip in both cases).
  const skippedCircumstances =
    eligibilityCircumstances == null ||
    (Array.isArray(eligibilityCircumstances) &&
      eligibilityCircumstances.length === 0)
  return (
    centrelinkSupport === false &&
    skippedCircumstances &&
    ((annualIncomeRange === 'OVER_155K' && dependants < 6) ||
      (annualIncomeRange === 'FROM_140K_TO_155K' && dependants < 5) ||
      (annualIncomeRange === 'FROM_115K_TO_139K' && dependants < 3) ||
      (annualIncomeRange === 'FROM_90K_TO_114K' && dependants < 1))
  )
}

FunctionFactory.Instance.register('meansIneligible', (params: unknown[]) =>
  meansIneligible(params[0], params[1], params[2], params[3])
)
