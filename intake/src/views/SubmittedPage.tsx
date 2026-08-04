import { LINKS } from '../consts'
import { useAnnouncePage } from './announce'

export const SubmittedPage = () => {
  const headingRef = useAnnouncePage("We've received your answers")
  return (
    <div className="intake-splash">
      <h1 tabIndex={-1} ref={headingRef}>
        <strong>Success!</strong> We&apos;ve received your answers
      </h1>
      <p>
        Our paralegals will contact you soon to discuss how we can help you.
      </p>
      <div className="intake-button-group">
        <a href={LINKS.HOME} className="d-btn d-btn-primary">
          Return home
        </a>
      </div>
    </div>
  )
}
