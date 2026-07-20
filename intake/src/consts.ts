// Client side routes. All paths are relative to the router basename
// (/intake/), which Django serves via a catch-all URL pattern.
export const ROUTES = {
  // The form itself lives at the root: it opens on a SurveyJS start page
  // (the welcome/intro screen) and the survey takes over from there.
  LANDING: '/',
  // Other splash pages
  SUBMITTED: '/submitted/',
  NO_EMAIL: '/no-email/',
  // Eligibility exit pages. Slugs name the exit reason in plain language under
  // a shared /ineligible/ prefix (one path family for analytics filtering) -
  // except VCAT representation, where the user opts not to continue rather
  // than being ruled ineligible, hence the /exit/ prefix.
  INELIGIBLE_OUTSIDE_VICTORIA: '/ineligible/outside-victoria/',
  INELIGIBLE_COMPENSATION: '/ineligible/compensation/',
  INELIGIBLE_INCOME: '/ineligible/income/',
  EXIT_VCAT_REPRESENTATION: '/exit/vcat-representation/',
  INELIGIBLE_REPAIRS_ORDER_OBTAINED: '/ineligible/repairs-order-obtained/',
  INELIGIBLE_NO_NOTICE_TO_VACATE: '/ineligible/no-notice-to-vacate/',
  INELIGIBLE_ALREADY_EVICTED: '/ineligible/already-evicted/',
  INELIGIBLE_URGENT_HEARING: '/ineligible/urgent-hearing/',
  INELIGIBLE_BOND_OUT_OF_SCOPE: '/ineligible/bond-out-of-scope/',
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
  TERMS_OF_USE: '/resources/terms-of-use/',
  PRIVACY_POLICY: '/resources/privacy-policy/',
  COLLECTIONS_STATEMENT: '/resources/collections-statement/',
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
