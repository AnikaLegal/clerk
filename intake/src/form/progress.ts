import { Model } from 'survey-core'

import { sectionIndexForPage, SUBMIT_PAGE } from '../questions'

// Direction of the last page change, used to slide the incoming page in from
// the side the user is travelling towards (forward -> from the right).
export type Direction = 'forward' | 'back'

// State for the progress indicator. section is -1 on the WELCOME and SUBMIT
// pages, which sit outside the sectioned flow, so both the stepper and the
// "Page x of y" count hide there. page / pageCount drive the count over the
// question pages; the leading WELCOME page (visible page 0) and the trailing
// SUBMIT page are both excluded from the total, so the first question reads as
// "Page 1" and the count never includes the final agreement page.
export const readProgress = (survey: Model) => {
  const name = survey.currentPage?.name
  return {
    name,
    section: name === SUBMIT_PAGE ? -1 : sectionIndexForPage(name),
    page: survey.currentPageNo,
    pageCount: survey.visiblePages.length - 2,
  }
}
