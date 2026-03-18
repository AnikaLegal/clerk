export const ROUTES = {
  // Splash pages
  LANDING: '/',
  LANDING_REPAIRS: '/repairs/',
  LANDING_COVID: '/covid/',
  LANDING_EVICTIONS: '/evictions/',
  INELIGIBLE: '/ineligible/',
  INELIGIBLE_NO_EVICTIONS_NOTICE: '/ineligible/no-notice/',
  INELIGIBLE_CHOICE: '/choice/',
  INELIGIBLE_MEANS: '/means/',
  INELIGIBLE_REPAIRS_APPLIED_VCAT: '/repairs-applied-vcat',
  INELIGIBLE_REPAIRS_GOTTEN_VCAT: '/repairs-gotten-vcat',
  INELIGIBLE_REPAIRS_VCAT_STAGE: '/repairs-vcat-stage',
  ASSESS_CIRCUMSTANCES: '/assess-circumstances/',
  INELIGIBLE_NOT_UNPAID_RENT: '/ineligible/not-unpaid/',
  INELIGIBLE_ALREADY_REMOVED: '/ineligible/already-removed/',
  INELIGIBLE_VCAT_HEARING: '/ineligible/vcat-hearing/',
  INELIGIBLE_EVICTED: '/ineligible/evicted',
  INELIGIBLE_WRONG_REASON: '/ineligible/wrong-reason',
  SUBMITTED: '/submitted/',
  NO_EMAIL: '/no-email/',
  BONDS_RECOVERY: '/bonds-recovery/',
  LEGAL_SCOPE_EVICTED: '/legal-scope-evicted/',
  LEGAL_SCOPE_COMPENSATION: '/legal-scope-compensation/',
  GEOGRAPHY: '/geography/',
  ABANDON: '/abandon/',
  NOT_FOUND: '/not-found/',
  RESUME: '/resume/',
  DOWNLOAD: '/download/',
  // Form pages
  FORM: '/intake/form/:qIdx/',
  build: (
    route: string,
    pathArgs: { [string]: any },
    qsArgs: { [string]: any }
  ): string => {
    let r = route
    for (let k of Object.keys(pathArgs)) {
      r = r.replace(k, pathArgs[k])
    }
    const qs = new URLSearchParams(qsArgs).toString()
    if (qs) {
      r = `${r}?${qs}`
    }
    return r
  },
}
