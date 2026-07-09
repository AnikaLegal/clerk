import { Model } from 'survey-core'

import { QUESTIONS } from '../questions'
import { Answers, AnswerValue, NONE_OF_THE_ABOVE, Upload } from './types'

// SurveyJS file question item shape (storeDataAsText: false).
interface SurveyFileItem {
  name: string
  type: string
  content: Upload
}

/**
 * Build the wire payload from survey state: the old form's tidyData
 * contract. Every non-display question the user has passed (visited) on a
 * currently-visible branch is included, with null for skipped/blank answers.
 * Questions never reached or on abandoned branches stay absent - the
 * backend does direct dict access on always-asked keys and .get() on branch
 * keys (core/services/submission.py).
 */
export const serializeAnswers = (
  survey: Model,
  visited: Set<string>
): Answers => {
  const answers: Answers = {}
  for (const q of QUESTIONS) {
    if (q.type === 'DISPLAY') continue
    const page = survey.getPageByName(q.name)
    if (!page || !page.isVisible || !visited.has(q.name)) continue
    let value = survey.getValue(q.name) as AnswerValue
    if (q.type === 'UPLOAD') {
      const items = (value ?? []) as unknown as SurveyFileItem[]
      value = items.map((item) => item.content)
    }
    if (value === NONE_OF_THE_ABOVE) {
      // Sentinel for choices whose wire value is null.
      value = null
    }
    answers[q.name] = value ?? null
  }
  return answers
}

/**
 * The inverse of serializeAnswers, used by the resume flow to seed survey
 * state from a stored submission.
 */
export const deserializeAnswers = (answers: Answers): Answers => {
  const data: Answers = {}
  for (const q of QUESTIONS) {
    if (q.type === 'DISPLAY') continue
    if (!(q.name in answers)) continue
    let value = answers[q.name]
    if (q.type === 'UPLOAD' && Array.isArray(value)) {
      value = (value as Upload[]).map((upload) => ({
        name: upload.file?.split('/').pop() ?? 'Uploaded file',
        type: '',
        content: upload,
      })) as unknown as Upload[]
    }
    if (value === null && q.choices?.length) {
      // Reverse the null sentinel mapping for choice questions that have a
      // null-valued option (WORK_OR_STUDY_CIRCUMSTANCES).
      const hasSentinel = q.choices.some((c) => c.value === NONE_OF_THE_ABOVE)
      if (hasSentinel) {
        value = NONE_OF_THE_ABOVE
      }
    }
    if (value === null) {
      // SurveyJS represents "no answer" as an absent key.
      continue
    }
    data[q.name] = value
  }
  return data
}
