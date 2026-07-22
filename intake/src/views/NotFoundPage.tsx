import { Link } from 'react-router-dom'

import { ROUTES } from '../consts'
import { useAnnouncePage } from './announce'

export const NotFoundPage = () => {
  const headingRef = useAnnouncePage('Page not found')
  return (
    <div className="intake-splash">
      <h1 tabIndex={-1} ref={headingRef}>
        Page not found
      </h1>
      <p>Sorry, we couldn't find that page.</p>
      <div className="intake-button-group">
        <Link to={ROUTES.LANDING} className="d-btn d-btn-primary">
          Go to the intake form
        </Link>
      </div>
    </div>
  )
}
