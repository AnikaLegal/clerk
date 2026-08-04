// Section groupings for the progress indicator: the previous intake form's six
// stages (Getting started / Getting in touch / ...) plus a final Submit step.
// Each page belongs to exactly one section; tests/sections.test.ts asserts the
// mapping covers every page in PAGES so it can't silently drift when pages are
// added or renamed.
export interface IntakeSection {
  label: string
  pages: string[]
}

export const SECTIONS: IntakeSection[] = [
  {
    label: 'Getting started',
    pages: [
      'ELIGIBILITY_ISSUE',
      'ELIGIBILITY_PRE_EVICTION',
      'ELIGIBILITY_LOCATION',
      'ELIGIBILITY_FINANCES',
      'ELIGIBILITY_MEANS_GATE',
      'ELIGIBILITY_MEANS_NOTES',
    ],
  },
  {
    label: 'Getting in touch',
    pages: ['ABOUT_EMAIL', 'ABOUT_NAME', 'ABOUT_CONTACT'],
  },
  {
    label: 'Your problem',
    pages: [
      'REPAIRS_ABOUT',
      'REPAIRS_STEPS',
      'REPAIRS_APPLIED',
      'EVICTION_STATUS',
      'EVICTION_HAS_NOTICE',
      'EVICTION_NOTICE',
      'EVICTION_NOTICE_TYPE',
      'EVICTION_REASON',
      'EVICTION_HEARING',
      'EVICTION_TERMINATION',
      'BONDS_MOVE_OUT',
      'BONDS_BOND',
      'BONDS_RTBA_APPLICATION',
      'BONDS_REASONS',
      'BONDS_DAMAGE',
      'BONDS_MONEY_OWED',
      'BONDS_CLEANING',
      'BONDS_LOCKS',
      'BONDS_OTHER',
    ],
  },
  {
    label: 'Your home',
    pages: ['PROPERTY_TENANCY', 'PROPERTY_ADDRESS'],
  },
  {
    label: 'Your landlord',
    pages: ['LANDLORD_AGENT', 'LANDLORD_DETAILS'],
  },
  {
    label: 'About you',
    pages: ['IMPACT_ABOUT', 'IMPACT_CIRCUMSTANCES', 'IMPACT_REFERRER'],
  },
  // The final agreement page gets its own step, so the stepper shows the whole
  // journey - including on the submit page itself, where every earlier section
  // is a click away.
  {
    label: 'Review & send',
    pages: ['SUBMIT'],
  },
]

const PAGE_TO_SECTION: Record<string, number> = {}
SECTIONS.forEach((section, index) => {
  section.pages.forEach((page) => {
    PAGE_TO_SECTION[page] = index
  })
})

// The index of the section a page belongs to, or -1 for pages outside the
// sectioned flow (e.g. the WELCOME start page).
export const sectionIndexForPage = (pageName: string | undefined): number =>
  pageName !== undefined && pageName in PAGE_TO_SECTION
    ? PAGE_TO_SECTION[pageName]
    : -1
