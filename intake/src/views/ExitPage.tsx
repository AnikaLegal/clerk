import { useLocation, useNavigate } from 'react-router-dom'

import { LINKS } from '../consts'
import { EXIT_PAGES } from './exit-content'

/**
 * Renders the eligibility exit splash for the current route. Answers stay in
 * localStorage, so "Go back" returns the user to the form mid-flow (matching
 * the old form, where exit pages were reachable-from navigations).
 */
export const ExitPage = () => {
  const location = useLocation()
  const navigate = useNavigate()
  const content = EXIT_PAGES[normalise(location.pathname)]
  if (!content) {
    return null
  }
  return (
    <div className="intake-splash">
      <h1>{content.title}</h1>
      {content.body}
      <div className="intake-button-group">
        <button
          className="intake-button intake-button-primary"
          onClick={() => navigate(-1)}
        >
          Go back
        </button>
        <a href={LINKS.HOME} className="intake-button">
          Return home
        </a>
      </div>
    </div>
  )
}

// Route keys in EXIT_PAGES have trailing slashes; the browser may not.
const normalise = (pathname: string): string =>
  pathname.endsWith('/') ? pathname : `${pathname}/`
