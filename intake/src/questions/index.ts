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
    <h2>
      By submitting this form, you are agreeing to our
      <a href="${LINKS.PRIVACY_POLICY}" target="_blank">Privacy Policy</a>,
      <a href="${LINKS.COLLECTIONS_STATEMENT}" target="_blank">Collections Statement</a>
      and website <a href="${LINKS.TERMS_OF_USE}" target="_blank">Terms of Use</a>.
    </h2>
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
