import { useLocation, useNavigate } from 'react-router-dom'

import { Offboard } from '../comps/Offboard'
import { LINKS, ROUTES } from '../consts'
import { useAnnouncePage } from './announce'
import { EXIT_PAGES, SplashExitContent } from './exit-content'

/**
 * Renders the eligibility exit page for the current route. Answers stay in
 * localStorage, so "Go back" returns the user to the form mid-flow (matching
 * the old form, where exit pages were reachable-from navigations).
 *
 * Pages are being migrated one at a time from the legacy splash layout onto
 * the offboarding template (see comps/Offboard); the content entry's shape
 * says which to render.
 */
export const ExitPage = () => {
  const location = useLocation()
  const content = EXIT_PAGES[normalise(location.pathname)]
  if (!content) {
    return null
  }
  if ('offboard' in content) {
    const { headline, explanation, body, primary, dataNote } = content.offboard
    return (
      <Offboard
        headline={headline}
        explanation={explanation}
        primary={primary}
        dataNote={dataNote}
      >
        {body}
      </Offboard>
    )
  }
  return <SplashExit content={content} />
}

const SplashExit = ({ content }: { content: SplashExitContent }) => {
  const navigate = useNavigate()
  const headingRef = useAnnouncePage(content.title)
  // Exit URLs are shareable, so a user can arrive with no in-app history (a
  // link from a caseworker, a new tab from browser history). navigate(-1) would
  // then do nothing or leave the site, so at the history floor go to the form
  // instead - it resumes from localStorage, landing them back where they were.
  const goBack = () => {
    const idx = (window.history.state as { idx?: number } | null)?.idx ?? 0
    if (idx === 0) {
      navigate(ROUTES.LANDING)
    } else {
      navigate(-1)
    }
  }
  return (
    <div className="intake-splash">
      <h1 tabIndex={-1} ref={headingRef}>
        {content.title}
      </h1>
      {content.body}
      <div className="intake-button-group">
        <button
          type="button"
          className="d-btn intake-btn-secondary"
          onClick={goBack}
        >
          Go back
        </button>
        <a href={LINKS.HOME} className="d-btn intake-btn-secondary">
          Return home
        </a>
      </div>
    </div>
  )
}

// Route keys in EXIT_PAGES have trailing slashes; the browser may not.
const normalise = (pathname: string): string =>
  pathname.endsWith('/') ? pathname : `${pathname}/`
