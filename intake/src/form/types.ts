// The question list is the source of truth for the form: SurveyJS renders it
// and evaluates visibility expressions, everything else (serialization,
// exits, side effects) is keyed off these definitions.

export type FieldType =
  | 'DISPLAY'
  | 'TEXT'
  | 'NUMBER'
  | 'EMAIL'
  | 'DATE'
  | 'CHOICE_SINGLE'
  | 'CHOICE_SINGLE_TEXT'
  | 'CHOICE_MULTI'
  | 'UPLOAD'
  | 'PHONE'
  | 'BOOLEAN'

export interface ChoiceOption {
  value: string | boolean
  text: string
}

export interface IntakeQuestion {
  // UPPER_SNAKE_CASE answer key, e.g. CENTRELINK_SUPPORT. Also used as the
  // SurveyJS page and question name. The backend keys off these names in
  // core/services/submission.py so they must not change.
  name: string
  type: FieldType
  required: boolean
  // Question prompt. May contain inline HTML (links etc), enabled via the
  // survey's onTextMarkdown handler.
  title?: string
  // DISPLAY questions only: HTML body rendered on its own page.
  html?: string
  // Help / guidance shown under the prompt. May contain inline HTML. Old
  // skip link copy ("I do not have an email address") lives here too.
  description?: string
  choices?: ChoiceOption[]
  // Number of columns for a choice question (radiogroup/checkbox). Set to 2 on
  // long lists so they render in two columns rather than running down the page.
  // Omit to keep the default single column.
  colCount?: number
  // SurveyJS visibility expression, e.g. "{ISSUES} = 'BONDS'". Replaces the
  // old form's askCondition functions.
  visibleIf?: string
  // SurveyJS conditional-required expression, e.g. "{ADDRESS_MANUAL} = true".
  // Used where a field's requiredness depends on another answer (the address
  // fields are only required when entered manually).
  requiredIf?: string
  // SurveyJS conditional-enabled expression. When false the question renders
  // read-only (e.g. the address fields are read-only unless entered manually).
  enableIf?: string
  // UI-only questions drive in-form behaviour (the address search box and its
  // manual-entry checkbox) but are never part of the wire payload - both
  // serializeAnswers and deserializeAnswers skip them.
  uiOnly?: boolean
  // Extra SurveyJS validators, e.g. the address search box's expression
  // validator requiring a suggestion to have been chosen.
  validators?: Record<string, unknown>[]
  // Value applied when the question is left blank on leaving its page, e.g.
  // NUMBER_OF_DEPENDENTS defaults to 0 (the old form's skip effect).
  skipDefault?: string | number | boolean
  // TEXT only: render a textarea instead of a single line input.
  multiline?: boolean
  placeholder?: string
  // Max characters for TEXT / EMAIL answers, mirroring the length of the DB
  // column the answer is written to (see core/services/submission.py) so a user
  // can't enter data that overflows the field when the submission is processed.
  maxLength?: number
  // Max value for NUMBER answers, for the same reason (e.g. POSTCODE fits its
  // 6-char column, WEEKLY_RENT fits its integer field).
  max?: number
  // Min value for NUMBER answers (e.g. dependants can't be negative).
  min?: number
}

// A group of questions rendered as a single SurveyJS panel: one visual block
// with a shared title (e.g. the home-address search + street/suburb/postcode
// fields). Purely presentational - the questions inside keep their own flat
// names and values, unlike a composite question.
export interface IntakePanel {
  panel: string
  title?: string
  questions: string[]
}

// A survey page groups one or more related questions. Questions keep their
// individual definitions (and element-level visibleIf); the page just decides
// which ones render together. `visibleIf` is a page-level guard used when
// every question on the page belongs to a single branch, so the whole page is
// skipped when that branch isn't taken.
export interface IntakePage {
  name: string
  visibleIf?: string
  // Ordered question names on the page (including any DISPLAY intros), with
  // panel groups inline where questions render as one block.
  questions: (string | IntakePanel)[]
}

// The page's question names in display order, with panel groups flattened.
export const pageQuestionNames = (page: IntakePage): string[] =>
  page.questions.flatMap((entry) =>
    typeof entry === 'string' ? entry : entry.questions
  )

import type { components } from '../api/types.generated'

// A file upload as returned by POST /api/upload/ and stored in answers.
export type Upload = components['schemas']['IntakeFileUpload']

export type AnswerValue = string | number | boolean | null | string[] | Upload[]

export type Answers = Record<string, AnswerValue>

// Sentinel for choices whose wire value is null (SurveyJS cannot hold null
// as an item value). Mapped to null in serializeAnswers.
export const NONE_OF_THE_ABOVE = 'NONE_OF_THE_ABOVE'
