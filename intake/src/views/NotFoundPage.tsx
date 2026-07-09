import { Link } from 'react-router-dom'

import { ROUTES } from '../consts'

export const NotFoundPage = () => (
  <div className="intake-splash">
    <h1>Page not found</h1>
    <p>Sorry, we couldn't find that page.</p>
    <div className="intake-button-group">
      <Link to={ROUTES.LANDING} className="intake-button intake-button-primary">
        Go to the intake form
      </Link>
    </div>
  </div>
)
