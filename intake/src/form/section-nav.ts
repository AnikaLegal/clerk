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

/**
 * Per-section status for the side navigation, derived - like navigableSections -
 * from the survey's visible pages, the visited set and the current answers.
 *
 * A section is `done` when every one of its visible pages lies behind the first
 * page of the form that cannot be passed: sections wholly behind the user
 * qualify, and one that is still fully answered after a backward jump keeps its
 * tick. The section holding the current page is `current` even when fully
 * answered, and everything ahead is `later`.
 */
export const readSectionStates = (
  survey: Model,
  visited: Set<string>
): SectionStatus[] => {
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

  return SECTIONS.map((section, index): SectionStatus => {
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
}

/**
 * The first still-visible page of a section, or undefined when the whole
 * section is on a branch the user isn't taking. Used by the submit-page answer
 * review to jump back into a section for editing, independent of whether the
 * section is currently "navigable" - the submit page's own section is the
 * current one (never offered as a forward jump), yet its answers still need an
 * Edit link, and from the submit page every section sits behind the user, so
 * the jump is always a valid backward move.
 */
export const firstVisiblePageOfSection = (
  survey: Model,
  sectionIndex: number
): string | undefined => {
  const section = SECTIONS[sectionIndex]
  if (!section) return undefined
  const visibleNames = new Set(survey.visiblePages.map((page) => page.name))
  return section.pages.find((name) => visibleNames.has(name))
}
