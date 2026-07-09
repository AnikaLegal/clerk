import { LINKS } from '../consts'

export const SubmittedPage = () => (
  <div className="intake-splash">
    <h1>
      <strong>Success!</strong> Your case has been submitted.
    </h1>
    <p>Our paralegals will contact you soon to discuss how we can help you.</p>
    <div className="intake-button-group">
      <a href={LINKS.HOME} className="intake-button intake-button-primary">
        Return home
      </a>
    </div>
  </div>
)
