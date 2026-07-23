import { Model } from 'survey-core'

import { QUESTIONS_BY_NAME } from '../questions'

interface PageElement {
  name: string
  isVisible: boolean
}

/**
 * Decide where a returning user re-enters the form and set survey.currentPage
 * accordingly. Restores the stored page when it is still visible; otherwise
 * (the stored page is on a branch no longer taken, or - after a server resume
 * via ResumePage - there is no stored page) lands on the first visible page
 * that still holds a question the user has not passed. A fresh visitor (empty
 * visited, no stored page) is left on the survey's default first page.
 *
 * The uiOnly exclusion is load-bearing for server resume: ResumePage seeds
 * visited from the wire answer keys, which never include the address search
 * box or manual-entry checkbox, so without it a resumed user with a completed
 * address would be dropped back on the property page.
 */
export const restorePosition = (
  survey: Model,
  visited: Set<string>,
  storedCurrentPage: string | null
): void => {
  if (storedCurrentPage) {
    const page = survey.getPageByName(storedCurrentPage)
    if (page && page.isVisible) {
      survey.currentPage = page
      return
    }
  }
  if (visited.size === 0) return
  const nextPage = survey.pages.find(
    (page) =>
      page.isVisible &&
      // page.questions (not .elements) so questions inside panels count.
      (page.questions as unknown as PageElement[]).some((el) => {
        const question = QUESTIONS_BY_NAME[el.name]
        // DISPLAY and uiOnly questions don't hold answers, so they can't make
        // a page count as unfinished (a server resume seeds visited from the
        // answers, which never include them).
        return (
          el.isVisible &&
          question &&
          question.type !== 'DISPLAY' &&
          !question.uiOnly &&
          !visited.has(el.name)
        )
      })
  )
  if (nextPage) {
    survey.currentPage = nextPage
  }
}
