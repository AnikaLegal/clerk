import { Model } from 'survey-core'

// Add the survey's custom navigation-bar items and return handles so the
// per-page sync (see useFormNavigation) can toggle their visibility and text.
export const addNavItems = (survey: Model) => {
  // A ghost "Review your answers" toggle shown only on the submit page, sitting
  // to the right of the Submit button. It discloses the answer-review panel;
  // its action, dynamic label and aria-expanded are wired in useFormNavigation
  // (they track the React state that renders the panel).
  const reviewToggleItem = survey.addNavigationItem({
    id: 'nav-review-toggle',
    title: 'Review your answers',
    innerCss: 'd-btn d-btn-ghost intake-review__toggle',
    visibleIndex: 900,
    visible: false,
    action: () => {},
  })
  return { reviewToggleItem }
}
