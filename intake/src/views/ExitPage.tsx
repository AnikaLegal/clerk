import { useLocation } from 'react-router-dom'

import { Offboard } from '../comps/Offboard'
import { EXIT_PAGES } from './exit-content'

/**
 * Renders the eligibility exit page for the current route on the offboarding
 * template (see comps/Offboard). Answers stay in localStorage, so the
 * template's "Go back" returns the user to the form mid-flow (matching the
 * old form, where exit pages were reachable-from navigations).
 */
export const ExitPage = () => {
  const location = useLocation()
  const content = EXIT_PAGES[normalise(location.pathname)]
  if (!content) {
    return null
  }
  return (
    <Offboard
      headline={content.headline}
      explanation={content.explanation}
      primary={content.primary}
      dataNote={content.dataNote}
    >
      {content.body}
    </Offboard>
  )
}

// Route keys in EXIT_PAGES have trailing slashes; the browser may not.
const normalise = (pathname: string): string =>
  pathname.endsWith('/') ? pathname : `${pathname}/`
