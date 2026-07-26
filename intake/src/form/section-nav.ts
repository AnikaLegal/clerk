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
    if (!question || question.type === 'DISPLAY' || question.uiOnly) continue
    if (!el.isVisible) continue
    if (!visited.has(el.name)) return false
    if (getExitRoute(el.name, survey.data as Answers)) return false
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
