import { Model, PageModel } from 'survey-core'

import { getExitRoute } from './exits'
import { Answers } from './types'
import { QUESTIONS_BY_NAME, SECTIONS, sectionIndexForPage } from '../questions'

interface PageElement {
  name: string
  isVisible: boolean
}

// Can the survey advance off this page? True when every visible real question
// on it has been passed (is in `visited`) and none of those answers now
// triggers an eligibility exit. This is what makes a forward jump safe: it only
// ever skips pages the user could have walked through with Next, so no exit,
// side effect, skip-default or required answer is bypassed. A question the user
// never reached - or one newly revealed by a later answer change - is not in
// `visited`, which correctly stops the run.
const canPassPage = (
  survey: Model,
  visited: Set<string>,
  page: PageModel
): boolean => {
  const elements = (page as unknown as { questions: PageElement[] }).questions
  for (const el of elements) {
    const question = QUESTIONS_BY_NAME[el.name]
    if (!question || question.type === 'DISPLAY') continue
    if (!el.isVisible) continue
    // A ui-only question can still carry an exit (the no-email checkbox), so
    // check that before skipping it - but it never holds a wire answer, so it
    // is not expected in `visited` (a server resume seeds visited from the
    // serialized answers, which exclude ui-only questions).
    if (getExitRoute(el.name, survey.data as Answers)) return false
    if (question.uiOnly) continue
    if (!visited.has(el.name)) return false
  }
  return true
}

/**
 * The sections the user can jump to from where they are now, mapped to the page
 * each jump lands on (the section's first still-visible page).
 *
 * A section is navigable when it is not the current one and its first visible
 * page is reachable - every page between here and that page is already passed
 * and exit-free, so the forward walk can land on it. Sections behind the
 * current page are always reachable (the user passed through them to get here)
 * and backward moves never trigger an exit, so they are always offered.
 * Sections ahead are offered as soon as their first page can be reached, so the
 * user can open a section before completing it. A still-unanswered question or
 * a triggered exit on the way shortens the run and holds back every section
 * whose start lies beyond it, so a jump can never skip something Next would
 * have stopped on.
 */
export const navigableSections = (
  survey: Model,
  visited: Set<string>
): Map<number, string> => {
  const result = new Map<number, string>()
  const pages = survey.visiblePages
  const currentIndex = pages.indexOf(survey.currentPage)
  if (currentIndex < 0) return result
  const currentSection = sectionIndexForPage(survey.currentPage?.name)
  const indexByName = new Map(pages.map((p, i) => [p.name, i]))

  // The first page from the current one forward that cannot be passed (an
  // unanswered required question or a now-triggered exit), or the end of the
  // form when everything ahead is complete.
  let frontier = currentIndex
  while (
    frontier < pages.length &&
    canPassPage(survey, visited, pages[frontier])
  ) {
    frontier++
  }

  SECTIONS.forEach((section, sectionIndex) => {
    if (sectionIndex === currentSection) return
    let firstVisible: string | null = null
    let firstVisibleIndex = -1
    for (const name of section.pages) {
      const idx = indexByName.get(name)
      if (idx === undefined) continue
      firstVisible = name
      firstVisibleIndex = idx
      break
    }
    // Whole section on a branch the user isn't taking - nothing to jump to.
    if (firstVisible === null) return
    // Reachable iff its first visible page is inside (or at the end of) the
    // passable run: frontier is the first page that cannot be passed, so a
    // first page at index <= frontier can still be landed on. Backward sections
    // satisfy this trivially (their first page precedes the current one);
    // forward ones as soon as the run reaches their start, whether or not the
    // rest of the section is answered.
    if (firstVisibleIndex <= frontier) result.set(sectionIndex, firstVisible)
  })
  return result
}

// Where the user stands in a section: behind it (and done with it), in it, or
// yet to reach it. Navigability is tracked separately (see SectionStatus): a
// later section can be reachable, and a done one momentarily not.
export type SectionState = 'done' | 'current' | 'later'

export interface SectionStatus {
  index: number
  label: string
  state: SectionState
  // Whether the section's answers are complete, independent of the state: the
  // current section is `current` even when fully answered, but its marker
  // should keep the completion tick rather than revert to a number.
  complete: boolean
  // Whether the section can be jumped into from here (never the current one).
  navigable: boolean
}

export interface FormStatus {
  sections: SectionStatus[]
  // Whole-form completion for the progress meter, 0-100. Every countable
  // section weighs the same: a complete one contributes a full share, the
  // current one the fraction of its pages passed - so the meter moves on every
  // page, not only at section boundaries.
  percent: number
  // How many sections are complete, for the "x of n done" summary.
  doneCount: number
  // The n in that summary, and the meter's denominator: the sections that can
  // actually complete. The final Review & send step holds no answers, so it
  // never reads done - counting it would leave the summary stuck at "n-1 of n"
  // and the meter short of full on the review page itself.
  sectionCount: number
}

/**
 * The whole form's status for the side navigation - per-section states plus the
 * progress meter's inputs - derived, like navigableSections, from the survey's
 * visible pages, the visited set and the current answers.
 *
 * A section is `done` when every one of its visible pages lies behind the first
 * page of the form that cannot be passed: sections wholly behind the user
 * qualify, and one that is still fully answered after a backward jump keeps its
 * tick. The section holding the current page is `current` even when fully
 * answered, and everything ahead is `later`.
 */
export const readFormStatus = (
  survey: Model,
  visited: Set<string>
): FormStatus => {
  const pages = survey.visiblePages
  const currentIndex = pages.indexOf(survey.currentPage)
  const currentSection = sectionIndexForPage(survey.currentPage?.name)
  const indexByName = new Map(pages.map((p, i) => [p.name, i]))
  const reachable = navigableSections(survey, visited)
  const pageAt = (name: string) => pages[indexByName.get(name) as number]

  // The first page of the whole form that cannot be passed - an unanswered
  // required question, or an answer that now triggers an eligibility exit - or
  // the end of the form when everything is answered. Nothing from there on is
  // complete: the run stops at that page, so a later section's answers, however
  // full, are no longer part of a finished form. Without this, going back and
  // choosing a disqualifying answer would leave every later section ticked.
  let frontier = 0
  while (
    frontier < pages.length &&
    canPassPage(survey, visited, pages[frontier])
  ) {
    frontier++
  }

  let doneCount = 0
  // The current section's share of the meter: the fraction of its pages the
  // user is past, or a full share once it is complete - a backward jump into
  // a finished form must not drain the meter.
  let currentFill = 0

  const sections = SECTIONS.map((section, index): SectionStatus => {
    const visiblePages = section.pages.filter((name) => indexByName.has(name))
    // A section holding no answers (the submit page is all display content) is
    // vacuously passable, so passability alone can't mark it done - it counts
    // only once the user is wholly past it.
    const holdsAnswers = visiblePages.some((name) => {
      const elements = (pageAt(name) as unknown as { questions: PageElement[] })
        .questions
      return elements.some((el) => {
        const question = QUESTIONS_BY_NAME[el.name]
        return (
          question &&
          question.type !== 'DISPLAY' &&
          !question.uiOnly &&
          el.isVisible
        )
      })
    })
    const whollyBehind =
      visiblePages.length > 0 &&
      visiblePages.every((name) => indexByName.get(name)! < currentIndex)
    const isDone =
      visiblePages.length > 0 &&
      (holdsAnswers || whollyBehind) &&
      visiblePages.every((name) => indexByName.get(name)! < frontier)
    if (isDone) doneCount += 1
    if (index === currentSection && !isDone) {
      const position = visiblePages.findIndex(
        (name) => indexByName.get(name) === currentIndex
      )
      currentFill =
        position > 0 ? position / Math.max(visiblePages.length, 1) : 0
    }
    return {
      index,
      label: section.label,
      state:
        index === currentSection
          ? 'current'
          : isDone
            ? 'done'
            : ('later' as const),
      complete: isDone,
      navigable: reachable.has(index),
    }
  })

  const sectionCount = SECTIONS.length - 1
  const percent = Math.min(
    100,
    Math.round(((doneCount + currentFill) / sectionCount) * 100)
  )
  return { sections, percent, doneCount, sectionCount }
}

// The per-section states alone (see readFormStatus).
export const readSectionStates = (
  survey: Model,
  visited: Set<string>
): SectionStatus[] => readFormStatus(survey, visited).sections
