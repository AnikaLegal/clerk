import { useNavigate } from 'react-router-dom'

import { LINKS } from '../consts'

export const AbandonPage = () => {
  const navigate = useNavigate()
  return (
    <div className="intake-splash">
      <h1>Are you sure you want to abandon your case?</h1>
      <p>
        Life can get busy quick and we appreciate the effort you have taken to
        start your journey with Anika. You are only a few steps away from
        creating a case and then we will take care of everything else.
      </p>
      <div className="intake-button-group">
        <button
          type="button"
          className="d-btn d-btn-primary"
          onClick={() => navigate(-1)}
        >
          Continue
        </button>
        <a href={LINKS.HOME}>
          <button type="button" className="d-btn d-btn-primary d-btn-soft">
            Abandon case
          </button>
        </a>
      </div>
    </div>
  )
}
