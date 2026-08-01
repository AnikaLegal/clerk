import { Model, Question } from 'survey-core'

import { QUESTIONS_BY_NAME, SECTIONS } from '../questions'

export interface AnswerRow {
  name: string
  label: string
  value: string
}

export interface SectionSummary {
  index: number
  label: string
  rows: AnswerRow[]
}

// A human-readable answer for the review list. SurveyJS's displayValue already
// maps choice values to their labels, joins multi-selects, and echoes free
// text / self-describe values, so lean on it; file uploads are the one type it
// renders unhelpfully (an object), so list the file names instead.
const formatValue = (question: Question): string => {
  if (question.getType() === 'file') {
    const files = question.value
    return Array.isArray(files)
      ? files.map((f) => f?.name ?? 'file').join(', ')
      : ''
  }
  const display = question.displayValue
  return typeof display === 'string' ? display : String(display ?? '')
}

// The question's prompt as a plain-text label: interpolate any {placeholders}
// (e.g. {RENT_IS}) against the current answers, then strip the inline HTML
// (e.g. <strong>) that some titles carry for their in-form rendering.
const labelFor = (survey: Model, title: string): string =>
  survey.processText(title, false).replace(/<[^>]+>/g, '')

/**
 * The user's answers grouped by section for the submit-page review, in section
 * and page order. Only visible, answered, value-holding questions are
 * included: DISPLAY (html) blocks and uiOnly helpers (the address search box
 * and manual-entry checkbox) hold no answer, hidden-branch questions aren't
 * shown, and skipped or blank ones are omitted. Sections with nothing answered
 * drop out entirely, so the review only lists what the user actually gave us.
 */
export const buildAnswerSummary = (survey: Model): SectionSummary[] => {
  const visibleNames = new Set(survey.visiblePages.map((page) => page.name))
  return SECTIONS.map((section, index) => {
    const rows: AnswerRow[] = []
    for (const pageName of section.pages) {
      if (!visibleNames.has(pageName)) continue
      const page = survey.getPageByName(pageName)
      if (!page) continue
      for (const question of page.questions) {
        const meta = QUESTIONS_BY_NAME[question.name]
        if (!meta || meta.type === 'DISPLAY' || meta.uiOnly) continue
        if (!question.isVisible || question.isEmpty()) continue
        rows.push({
          name: question.name,
          label: labelFor(survey, meta.title ?? question.name),
          value: formatValue(question),
        })
      }
    }
    return { index, label: section.label, rows }
  }).filter((section) => section.rows.length > 0)
}
