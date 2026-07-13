// Client side routes. All paths are relative to the router basename
// (/intake/), which Django serves via a catch-all URL pattern.
export const ROUTES = {
  // The form itself lives at the root: it opens on a SurveyJS start page
  // (the welcome/intro screen) and the survey takes over from there.
  LANDING: '/',
  // Other splash pages
  SUBMITTED: '/submitted/',
  NO_EMAIL: '/no-email/',
  // Eligibility exit pages
  GEOGRAPHY: '/geography/',
  LEGAL_SCOPE_COMPENSATION: '/legal-scope-compensation/',
  INELIGIBLE_MEANS: '/means/',
  INELIGIBLE_REPAIRS_APPLIED_VCAT: '/repairs-applied-vcat/',
  INELIGIBLE_REPAIRS_GOTTEN_VCAT: '/repairs-gotten-vcat/',
  INELIGIBLE_NO_EVICTIONS_NOTICE: '/ineligible/no-notice/',
  INELIGIBLE_ALREADY_REMOVED: '/ineligible/already-removed/',
  INELIGIBLE_VCAT_HEARING: '/ineligible/vcat-hearing/',
  BONDS_RECOVERY: '/bonds-recovery/',
  RESUME: '/resume/',
} as const

export const API_URLS = {
  SUBMISSION: '/api/submission/',
  UPLOAD: '/api/upload/',
  NO_EMAIL: '/api/webhooks/intake-noemail/',
} as const

// The form is served from the main site, so links that used to point at
// ${SERVER} in the old intake repo are now same-origin relative paths.
// These are full page navigations to the Django/Wagtail site, not client
// side routes.
export const LINKS = {
  HOME: '/',
  SERVICES: '/services/',
  TERMS_OF_USE: '/resources/terms-of-use/',
  PRIVACY_POLICY: '/resources/privacy-policy/',
  COLLECTIONS_STATEMENT: '/resources/collections-statement/',
  ELIGIBILITY_PAGE: '/resources/eligibility-criteria/',
  EVICTION_INFO: '/services/eviction-support/',
  REPAIRS_INFO: '/services/rental-repairs/',
  BONDS_INFO: '/services/bond-recovery/',
  BONDS_RESOURCES: '/blog/bonds-and-bond-recovery/',
  VIC_LEGAL_AID: 'https://legalaid.vic.gov.au/',
  EVICTIONS_AND_POSSESSION_ORDERS_INFO:
    'https://consumer.vic.gov.au/housing/renting/moving-out-giving-notice-and-evictions/evictions-and-immediate-notice/evictions-and-possession-orders',
} as const

// localStorage key for in-progress form state.
export const STORAGE_KEY = 'anika-intake-form'
