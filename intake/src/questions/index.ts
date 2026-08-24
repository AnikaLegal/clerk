import { LINKS } from '../consts'
import { IntakeQuestion } from '../form/types'
import { ABOUT_QUESTIONS } from './about'
import { ELIGIBILITY_QUESTIONS } from './eligibility'
import { IMPACT_QUESTIONS } from './impact'
import { BONDS_QUESTIONS } from './issues/bonds'
import { EVICTION_RETALIATORY_QUESTIONS } from './issues/eviction-retaliatory'
import { REPAIRS_QUESTIONS } from './issues/repairs'
import { LANDLORD_QUESTIONS } from './landlord'
import { PROPERTY_QUESTIONS } from './property'

// Final agreement page: the survey's Complete button performs the submit.
const SUBMIT_QUESTION: IntakeQuestion = {
  name: 'SUBMIT',
  type: 'DISPLAY',
  required: false,
  html: `
    <h2>Ready to send</h2>
    <p>
      One of our team will contact you in a few business days to talk about
      how we can help. You can check your answers first if you'd like to.
    </p>
  `,
}

// The answers, collapsed behind a row that says what is inside them (see
// comps/AnswerReview). Sending stays available without opening it.
const REVIEW_QUESTION: IntakeQuestion = {
  name: 'REVIEW',
  type: 'REVIEW',
  required: false,
  // Never serialized: it holds no answer of its own.
  uiOnly: true,
}

// The declaration, below the review so it sits directly above the send button.
const AGREEMENT_QUESTION: IntakeQuestion = {
  name: 'AGREEMENT',
  type: 'DISPLAY',
  required: false,
  html: `
    <p>
      By sending us your answers, you are agreeing to our
      <a href="${LINKS.PRIVACY_POLICY}" target="_blank">Privacy Policy</a>,
      <a href="${LINKS.COLLECTIONS_STATEMENT}" target="_blank">Collections Statement</a>
      and website <a href="${LINKS.TERMS_OF_USE}" target="_blank">Terms of Use</a>.
    </p>
  `,
}

// All questions in the questionnaire, in presentation order (one per page).
// Same composition order as the old repo's questions/index.js, minus the
// unreachable EVICTION_ARREARS branch which was deliberately dropped.
export const QUESTIONS: IntakeQuestion[] = [
  ...ELIGIBILITY_QUESTIONS,
  ...ABOUT_QUESTIONS,
  ...REPAIRS_QUESTIONS,
  ...EVICTION_RETALIATORY_QUESTIONS,
  ...BONDS_QUESTIONS,
  ...PROPERTY_QUESTIONS,
  ...LANDLORD_QUESTIONS,
  ...IMPACT_QUESTIONS,
  SUBMIT_QUESTION,
  REVIEW_QUESTION,
  AGREEMENT_QUESTION,
]

export const QUESTIONS_BY_NAME: Record<string, IntakeQuestion> =
  Object.fromEntries(QUESTIONS.map((q) => [q.name, q]))

export {
  PAGES,
  PAGE_BY_NAME,
  BONDS_MOVE_OUT_PAGE,
  EMAIL_PAGE,
  SUBMIT_PAGE,
} from './pages'
export { SECTIONS, sectionIndexForPage } from './sections'
