import { Link } from 'react-router-dom'

import { ROUTES } from '../consts'

export const NotFoundPage = () => (
  <div className="intake-splash">
    <h1>Page not found</h1>
    <p>Sorry, we couldn't find that page.</p>
    <div className="intake-button-group">
      <Link to={ROUTES.LANDING}>
        <button type="button" className="d-btn d-btn-primary">
          Go to the intake form
        </button>
      </Link>
    </div>
  </div>
)
