import { Link } from 'react-router-dom'

import logoUrl from '../assets/logo-color.svg'
import { ROUTES } from '../consts'

// Minimal chrome above the survey: logo plus a close button that routes to
// the abandon interstitial (progress is kept in localStorage).
export const Header = () => (
  <header className="intake-header">
    <Link to={ROUTES.LANDING}>
      <img src={logoUrl} alt="Anika Legal" className="intake-header-logo" />
    </Link>
    <Link
      to={ROUTES.ABANDON}
      className="intake-header-close"
      aria-label="Close the form"
    >
      &times;
    </Link>
  </header>
)
