import { Link } from 'react-router-dom'

import { events } from '../analytics'
import logoUrl from '../assets/logo-color.svg'
import { LINKS, ROUTES } from '../consts'

export const LandingPage = () => (
  <div className="intake-splash">
    <img src={logoUrl} alt="Anika Legal" className="intake-splash-logo" />
    <h1>Welcome to the Anika Legal intake form!</h1>
    <p>
      We're here to help you with your rental problem. In order for us to help
      you, we need to ask you a series of simple questions to see whether you're
      eligible. This questionnaire takes approximately 10 minutes to complete.
    </p>
    <p>
      Before starting the intake form, please have the information ready about:
    </p>
    <ul>
      <li>Your rental property</li>
      <li>Your rental provider</li>
      <li>Your agent, if applicable</li>
      <li>Your income</li>
    </ul>
    <p>
      You can have a look at our{' '}
      <a href={LINKS.COLLECTIONS_STATEMENT}>collection statement</a> if you have
      any questions about why we need your information, and what we do with it.
    </p>
    <div className="intake-button-group">
      <Link
        to={ROUTES.FORM}
        className="intake-button intake-button-primary"
        onClick={events.onStartIntake}
      >
        Let's get started
      </Link>
      <a href={LINKS.SERVICES} className="intake-button">
        Learn more
      </a>
    </div>
  </div>
)
