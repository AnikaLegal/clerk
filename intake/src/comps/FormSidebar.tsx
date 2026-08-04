import { useEffect, useMemo } from 'react'
import { createTOCListModel, getTocRootCss, Model } from 'survey-core'
import { List } from 'survey-react-ui'

/**
 * The form's side navigation, built on SurveyJS's table of contents.
 *
 * createTOCListModel gives us the same list the built-in TOC uses (one entry
 * per visible page, kept in step with the current page, each entry navigating
 * on click), but as a plain model we render ourselves - so the list sits in our
 * own column beside the question card rather than inside the survey root, and
 * its contents and styling are ours to shape from here.
 *
 * Currently the SurveyJS default: page navigation titles, which fall back to
 * page names, and entries that navigate straight to their page.
 */
export const FormSidebar = ({ survey }: { survey: Model }) => {
  // The list subscribes to the survey (current page, page list), so it is built
  // once per survey and disposed with the component.
  const list = useMemo(() => createTOCListModel(survey), [survey])
  useEffect(() => () => list.dispose(), [list])

  return (
    <nav className="intake-sidebar" aria-label="Form navigation">
      {/* The rail is banded like the question column: a head, the list, and a
          foot whose hairline continues the one above the Back / Continue
          buttons. Head and foot are empty for now - the progress summary and
          the save-and-finish-later action land in them later. */}
      <div className="intake-sidebar__head" />
      <div className="intake-sidebar__list">
        <div className={getTocRootCss(survey)}>
          <List model={list} />
        </div>
      </div>
      <div className="intake-sidebar__foot" />
    </nav>
  )
}
