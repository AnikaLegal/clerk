import { NavigateFunction } from 'react-router-dom'
import { Model } from 'survey-core'

import { events } from '../analytics'
import { ROUTES } from '../consts'

// Add the survey's three custom navigation-bar items and return handles so the
// per-page sync (see useFormNavigation) can toggle their visibility and text.
export const addNavItems = (survey: Model, navigate: NavigateFunction) => {
  // A dedicated "I don't have an email address" navigation button that routes
  // to the no-email contact fallback. It sits in the survey's navigation bar
  // beside Previous / Next and is shown only while the email page is current.
  const noEmailItem = survey.addNavigationItem({
    id: 'nav-no-email',
    title: "I don't have an email address",
    innerCss: 'd-btn intake-btn-secondary',
    visible: false,
    action: () => {
      events.onFormExit({
        question: 'NO_EMAIL_BUTTON',
        route: ROUTES.NO_EMAIL,
      })
      navigate(ROUTES.NO_EMAIL)
    },
  })
  // Its sibling on the bonds move-out date page: users who are not moving out
  // exit to the bond-recovery resources page instead of answering the
  // (required) date question.
  const notMovingOutItem = survey.addNavigationItem({
    id: 'nav-not-moving-out',
    title: "I'm not moving out",
    innerCss: 'd-btn intake-btn-secondary',
    visible: false,
    action: () => {
      events.onFormExit({
        question: 'NOT_MOVING_OUT_BUTTON',
        route: ROUTES.INELIGIBLE_BOND_OUT_OF_SCOPE,
      })
      navigate(ROUTES.INELIGIBLE_BOND_OUT_OF_SCOPE)
    },
  })
  // A non-interactive "Page x of y" count rendered at the far right of the
  // navigation bar, vertically centred with the Previous / Next buttons. Its
  // wrapper is pushed right and its button styling stripped to plain text in
  // global.css; disableTabStop keeps it out of the keyboard tab order. A high
  // visibleIndex keeps it last so the right-push separates only it.
  const pageCountItem = survey.addNavigationItem({
    id: 'nav-page-count',
    title: '',
    css: 'intake-page-count',
    innerCss: 'intake-page-count__text',
    disableTabStop: true,
    visibleIndex: 1000,
    visible: false,
    action: () => {},
  })
  // A ghost "Review your answers" toggle shown only on the submit page, sitting
  // to the right of the Submit button. It discloses the answer-review panel;
  // its action, dynamic label and aria-expanded are wired in useFormNavigation
  // (they track the React state that renders the panel). A visibleIndex below
  // the page count's keeps it left of that (though the count is hidden here).
  const reviewToggleItem = survey.addNavigationItem({
    id: 'nav-review-toggle',
    title: 'Review your answers',
    innerCss: 'd-btn d-btn-ghost intake-review__toggle',
    visibleIndex: 900,
    visible: false,
    action: () => {},
  })
  return { noEmailItem, notMovingOutItem, pageCountItem, reviewToggleItem }
}
