import { Model, PageModel } from 'survey-core'

import { getExitRoute } from './exits'
import { SubmissionSaver } from './save'
import { serializeAnswers } from './serialize'
import { runSideEffect } from './side-effects'
import { Answers } from './types'
import { QUESTIONS_BY_NAME } from '../questions'

interface PageElement {
  name: string
  isVisible: boolean
}

const isBlank = (value: unknown): boolean =>
  value === undefined ||
  value === null ||
  value === '' ||
  (Array.isArray(value) && value.length === 0)

// Names of the questions currently visible on a page, in display order. A
// hidden conditional question is excluded so its side effect / exit predicate
// isn't evaluated against an absent answer.
const visibleNames = (page: { questions: PageElement[] }): string[] =>
  page.questions.filter((el) => el.isVisible).map((el) => el.name)

export interface PageAdvance {
  answers: Answers
  // The route and the question that triggered it if a question on the page
  // disqualifies the user, else null.
  exit: { route: string; question: string } | null
}

// The forward pipeline for advancing off a page: apply skip defaults to blank
// questions (e.g. dependants -> 0), mark every question on the page as passed,
// then run each question's side effect and check its exit in page order. The
// first matching exit wins (later questions are treated as not reached, as they
// would be one-per-page). Mutates survey values and the visited set; the caller
// owns navigation and persistence.
export const applyPageAdvance = (
  survey: Model,
  page: PageModel,
  visited: Set<string>,
  saver: SubmissionSaver
): PageAdvance => {
  const names = visibleNames(page as unknown as { questions: PageElement[] })
  // Apply skip defaults for questions left blank and record every question on
  // the page as passed.
  for (const name of names) {
    const question = QUESTIONS_BY_NAME[name]
    if (!question || question.type === 'DISPLAY') continue
    if (question.skipDefault !== undefined && isBlank(survey.getValue(name))) {
      survey.setValue(name, question.skipDefault)
    }
    visited.add(name)
  }
  const answers = serializeAnswers(survey, visited)
  for (const name of names) {
    runSideEffect(name, { answers, saver })
    const route = getExitRoute(name, survey.data as Answers)
    if (route) return { answers, exit: { route, question: name } }
  }
  return { answers, exit: null }
}
