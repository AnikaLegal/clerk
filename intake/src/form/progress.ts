import { Model } from 'survey-core'

import { sectionIndexForPage } from '../questions'

// Direction of the last page change, used to slide the incoming page in from
// the side the user is travelling towards (forward -> from the right).
export type Direction = 'forward' | 'back'

// State for the progress indicator. section is -1 on the WELCOME page, which
// sits outside the sectioned flow, so the stepper hides there; the SUBMIT page
// is the final "Submit" section, so the stepper shows the completed journey on
// it. page / pageCount drive the "Page x of y" count over the question pages;
// the leading WELCOME page (visible page 0) and the trailing SUBMIT page are
// both excluded from the total, so the first question reads as "Page 1" and
// the count never includes the final agreement page (on it, page exceeds
// pageCount and the count is hidden - see useFormNavigation's syncPage).
export const readProgress = (survey: Model) => {
  const name = survey.currentPage?.name
  return {
    name,
    section: sectionIndexForPage(name),
    page: survey.currentPageNo,
    pageCount: survey.visiblePages.length - 2,
  }
}
