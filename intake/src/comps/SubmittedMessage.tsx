import { LINKS } from '../consts'
import { useAnnouncePage } from '../views/announce'

/**
 * The confirmation shown once the answers are in: what happened, what comes
 * next, and a way out of the form. Rendered inside the form's card as its last
 * step, so the form ends where it ran (see FormPage).
 */
export const SubmittedMessage = () => {
  const headingRef = useAnnouncePage("We've received your answers")
  return (
    <>
      <h1 tabIndex={-1} ref={headingRef}>
        We&apos;ve received your answers
      </h1>
      <p>
        Our paralegals will contact you soon to discuss how we can help you.
      </p>
      {/* The way out, as a text link rather than a button - nothing here needs
          doing, so it shouldn't read as an action (the same treatment the
          offboarding pages give their escape links). */}
      <a className="intake-home-link" href={LINKS.HOME}>
        Go to the Anika Legal home page
      </a>
    </>
  )
}
