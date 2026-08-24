import { IntakePage } from '../form/types'

// The email question lives on its own page with its no-email escape hatch: a
// checkbox that disables the field and exits to the contact fallback on
// Continue (see questions/about.ts and form/exits.ts).
export const EMAIL_PAGE = 'ABOUT_EMAIL'

// The final agreement page. Its Submit button performs the submit; it is not
// shown in or counted by the "Page x of y" progress (see views/FormPage.tsx).
export const SUBMIT_PAGE = 'SUBMIT'

// The bonds move-out date lives on its own page with its not-moving-out
// escape hatch: a checkbox that disables the date and exits to the
// bond-recovery resources page on Continue (see questions/issues/bonds.ts
// and form/exits.ts).
export const BONDS_MOVE_OUT_PAGE = 'BONDS_MOVE_OUT'

// Branch guard expressions, kept in step with the question-level visibleIf
// values in the modules below. When every question on a page shares a branch
// condition, the page carries it so SurveyJS skips the whole page off-branch.
const IS_REPAIRS = "{ISSUES} = 'REPAIRS'"
const IS_EVICTION = "{ISSUES} = 'EVICTION_RETALIATORY'"
const IS_BONDS = "{ISSUES} = 'BONDS'"
const IS_BONDS_WITH_APPLICATION = `${IS_BONDS} and {BONDS_HAS_LANDLORD_MADE_RTBA_APPLICATION} = true`
const isClaimReason = (reason: string) =>
  `${IS_BONDS_WITH_APPLICATION} and {BONDS_CLAIM_REASONS} contains '${reason}'`
const MEANS_INELIGIBLE =
  'meansIneligible({CENTRELINK_SUPPORT}, {ELIGIBILITY_CIRCUMSTANCES}, {ANNUAL_INCOME_RANGE}, {NUMBER_OF_DEPENDENTS})'

// The form as a sequence of pages, each holding a small group of related
// questions. Question order matches the flat QUESTIONS list (pages are
// consecutive chunks), so the flow the user walks is unchanged - only the
// page boundaries move. Gate questions that can eject the user, and the
// means-test prompts, stay on their own pages so the user isn't asked to fill
// a required follow-up they're about to be exited past.
export const PAGES: IntakePage[] = [
  // Eligibility
  { name: 'ELIGIBILITY_ISSUE', questions: ['INTRO', 'ISSUES'] },
  {
    name: 'ELIGIBILITY_PRE_EVICTION',
    visibleIf: IS_EVICTION,
    questions: ['PRE_EVICTION_NOTICE'],
  },
  { name: 'ELIGIBILITY_LOCATION', questions: ['IS_VICTORIAN_TENANT'] },
  {
    name: 'ELIGIBILITY_FINANCES',
    questions: [
      'ELIGIBILITY_INTRO',
      'CENTRELINK_SUPPORT',
      'ANNUAL_INCOME_RANGE',
      'NUMBER_OF_DEPENDENTS',
      'ELIGIBILITY_CIRCUMSTANCES',
    ],
  },
  {
    name: 'ELIGIBILITY_MEANS_GATE',
    visibleIf: MEANS_INELIGIBLE,
    questions: ['INELIGIBLE_CHOICE'],
  },
  {
    name: 'ELIGIBILITY_MEANS_NOTES',
    visibleIf: MEANS_INELIGIBLE,
    questions: ['ELIGIBILITY_NOTES'],
  },

  // Getting in touch
  { name: EMAIL_PAGE, questions: ['EMAIL', 'NO_EMAIL'] },
  {
    name: 'ABOUT_NAME',
    questions: ['FIRST_NAME', 'LAST_NAME', 'PREFERRED_NAME'],
  },
  { name: 'ABOUT_CONTACT', questions: ['PHONE', 'AVAILABILITY'] },

  // Repairs branch
  {
    name: 'REPAIRS_ABOUT',
    visibleIf: IS_REPAIRS,
    questions: ['REPAIRS_INTRO', 'REPAIRS_ISSUE_PHOTO', 'REPAIRS_ISSUE_START'],
  },
  {
    name: 'REPAIRS_STEPS',
    visibleIf: IS_REPAIRS,
    questions: ['REPAIRS_VCAT'],
  },
  {
    // Only reached when the user applied to VCAT (and wasn't ejected for
    // already holding an order): the continue-or-not gate stands alone, so a
    // user being ejected off REPAIRS_STEPS is never asked to answer it first.
    name: 'REPAIRS_APPLIED',
    visibleIf: `${IS_REPAIRS} and {REPAIRS_VCAT} contains 'APPLIED_VCAT'`,
    questions: ['REPAIRS_APPLIED_VCAT'],
  },

  // Eviction branch
  {
    name: 'EVICTION_STATUS',
    visibleIf: IS_EVICTION,
    questions: [
      'EVICTION_RETALIATORY_INTRO',
      'EVICTION_RETALIATORY_IS_ALREADY_REMOVED',
    ],
  },
  {
    name: 'EVICTION_HAS_NOTICE',
    visibleIf: IS_EVICTION,
    questions: ['EVICTION_RETALIATORY_HAS_NOTICE'],
  },
  {
    name: 'EVICTION_NOTICE',
    visibleIf: IS_EVICTION,
    questions: [
      'EVICTION_RETALIATORY_DOCUMENTS_UPLOAD',
      'EVICTION_RETALIATORY_DATE_RECEIVED_NTV',
    ],
  },
  {
    name: 'EVICTION_NOTICE_TYPE',
    visibleIf: IS_EVICTION,
    questions: ['EVICTION_RETALIATORY_NTV_TYPE'],
  },
  {
    name: 'EVICTION_REASON',
    visibleIf: IS_EVICTION,
    questions: [
      'EVICTION_RETALIATORY_RETALIATORY_REASON',
      'EVICTION_RETALIATORY_RETALIATORY_REASON_OTHER',
    ],
  },
  {
    name: 'EVICTION_HEARING',
    visibleIf: IS_EVICTION,
    // The hearing date can eject the user (a hearing within a fortnight), so
    // only its own gate question shares the page; the termination date lives
    // on the next page, reached only by users who are continuing.
    questions: [
      'EVICTION_RETALIATORY_VCAT_HEARING',
      'EVICTION_RETALIATORY_VCAT_HEARING_DATE',
    ],
  },
  {
    name: 'EVICTION_TERMINATION',
    visibleIf: IS_EVICTION,
    questions: ['EVICTION_RETALIATORY_TERMINATION_DATE'],
  },

  // Bonds branch
  {
    name: BONDS_MOVE_OUT_PAGE,
    visibleIf: IS_BONDS,
    questions: ['BONDS_INTRO', 'BONDS_MOVE_OUT_DATE', 'NOT_MOVING_OUT'],
  },
  {
    name: 'BONDS_BOND',
    visibleIf: IS_BONDS,
    questions: ['BOND_RTBA'],
  },
  {
    name: 'BONDS_RTBA_APPLICATION',
    visibleIf: IS_BONDS,
    questions: [
      'BONDS_HAS_LANDLORD_MADE_RTBA_APPLICATION',
      'BONDS_TENANT_HAS_RTBA_APPLICATION_COPY',
      'BONDS_RTBA_APPLICATION_UPLOAD',
    ],
  },
  {
    name: 'BONDS_REASONS',
    visibleIf: IS_BONDS_WITH_APPLICATION,
    questions: ['BONDS_CLAIM_REASONS'],
  },
  {
    name: 'BONDS_DAMAGE',
    visibleIf: isClaimReason('Damage'),
    questions: [
      'BONDS_DAMAGE_INTRO',
      'BONDS_DAMAGE_CLAIM_DESCRIPTION',
      'BONDS_DAMAGE_CLAIM_AMOUNT',
      'BONDS_DAMAGE_CAUSED_BY_TENANT',
      'BONDS_DAMAGE_QUOTE_UPLOAD',
    ],
  },
  {
    name: 'BONDS_MONEY_OWED',
    visibleIf: isClaimReason('Rent or other money owing'),
    questions: [
      'BONDS_MONEY_OWED_INTRO',
      'BONDS_MONEY_OWED_CLAIM_DESCRIPTION',
      'BONDS_MONEY_OWED_CLAIM_AMOUNT',
      'BONDS_MONEY_IS_OWED_BY_TENANT',
    ],
  },
  {
    name: 'BONDS_CLEANING',
    visibleIf: isClaimReason('Cleaning'),
    questions: [
      'BONDS_CLEANING_INTRO',
      'BONDS_CLEANING_CLAIM_DESCRIPTION',
      'BONDS_CLEANING_CLAIM_AMOUNT',
      'BONDS_CLEANING_DOCUMENT_UPLOADS',
    ],
  },
  {
    name: 'BONDS_LOCKS',
    visibleIf: isClaimReason('Locks and security devices'),
    questions: [
      'BONDS_LOCKS_INTRO',
      'BONDS_LOCKS_CLAIM_AMOUNT',
      'BONDS_LOCKS_CHANGED_BY_TENANT',
      'BONDS_LOCKS_CHANGE_QUOTE',
    ],
  },
  {
    name: 'BONDS_OTHER',
    visibleIf: isClaimReason('Other reason'),
    questions: [
      'BONDS_OTHER_INTRO',
      'BONDS_OTHER_REASONS_DESCRIPTION',
      'BONDS_OTHER_REASONS_AMOUNT',
    ],
  },

  // Rental property
  {
    name: 'PROPERTY_TENANCY',
    questions: [
      'PROPERTY_INTRO',
      'PROPERTY_INTRO_BONDS',
      'RENTAL_CIRCUMSTANCES',
      'IS_ON_LEASE',
      'START_DATE',
    ],
  },
  {
    name: 'PROPERTY_ADDRESS',
    questions: [
      'ADDRESS_INTRO',
      'ADDRESS_SEARCH',
      'ADDRESS_MANUAL',
      'ADDRESS',
      'SUBURB',
      'POSTCODE',
      'WEEKLY_RENT',
    ],
  },

  // Landlord
  {
    name: 'LANDLORD_AGENT',
    questions: [
      'PROPERTY_MANAGER_INTRO',
      'PROPERTY_MANAGER_IS_AGENT',
      'AGENT_NAME',
      'AGENT_ADDRESS',
      'AGENT_EMAIL',
      'AGENT_PHONE',
    ],
  },
  {
    name: 'LANDLORD_DETAILS',
    questions: [
      'LANDLORD_NAME',
      'LANDLORD_ADDRESS',
      'LANDLORD_EMAIL',
      'LANDLORD_PHONE',
    ],
  },

  // About you (personal details)
  {
    name: 'IMPACT_ABOUT',
    questions: [
      'IMPACT_INTRO',
      'DOB',
      'GENDER',
      'IS_ABORIGINAL_OR_TORRES_STRAIT_ISLANDER',
    ],
  },
  {
    name: 'IMPACT_CIRCUMSTANCES',
    questions: [
      'CAN_SPEAK_NON_ENGLISH',
      'INTERPRETER',
      'FIRST_LANGUAGE',
      'WORK_OR_STUDY_CIRCUMSTANCES',
    ],
  },
  {
    name: 'IMPACT_REFERRER',
    questions: [
      'REFERRER_TYPE',
      'LEGAL_CENTRE_REFERRER',
      'HOUSING_SERVICE_REFERRER',
      'COMMUNITY_ORGANISATION_REFERRER',
      'SOCIAL_REFERRER',
    ],
  },

  // Review + agreement + send
  { name: SUBMIT_PAGE, questions: ['SUBMIT', 'REVIEW', 'AGREEMENT'] },
]

export const PAGE_BY_NAME: Record<string, IntakePage> = Object.fromEntries(
  PAGES.map((p) => [p.name, p])
)
