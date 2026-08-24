import { LINKS } from '../consts'
import { useAnnouncePage } from './announce'

// The post-submit view: saving in progress, an unrecoverable failure
// (permanent), or a retryable connection / server failure (transient).
export type SubmitState = 'submitting' | 'permanent' | 'transient'

const SUBMIT_TITLES: Record<SubmitState, string> = {
  submitting: 'Sending your answers',
  permanent: "We couldn't send your answers",
  transient: 'Something went wrong',
}

// Renders the post-submit splash. Shares the splash chrome and typography with
// the exit / submitted pages; centred vertically in its band (intake-splash--
// centred) since it is a single short message rather than a full page. The
// heading takes focus on show, like the other splash routes.
export const SubmitStatus = ({
  state,
  onRetry,
}: {
  state: SubmitState
  onRetry: () => void
}) => {
  const headingRef = useAnnouncePage(SUBMIT_TITLES[state])
  return (
    <div className="intake-splash intake-splash--centred">
      {state === 'submitting' && (
        <h1 tabIndex={-1} ref={headingRef}>
          Sending your answers...
        </h1>
      )}
      {state === 'permanent' && (
        <>
          <h1 tabIndex={-1} ref={headingRef}>
            Sorry, we couldn&apos;t send your answers
          </h1>
          <p>
            Trying again won&apos;t fix it. Please email{' '}
            <a href={LINKS.CONTACT}>tech@anikalegal.org.au</a> - your answers
            are still saved on this device.
          </p>
        </>
      )}
      {state === 'transient' && (
        <>
          <h1 tabIndex={-1} ref={headingRef}>
            Sorry, something went wrong
          </h1>
          <p>
            We could not send your answers. Please check your connection and try
            again.
          </p>
          <div className="intake-button-group">
            <button
              type="button"
              className="d-btn d-btn-primary"
              onClick={onRetry}
            >
              Try again
            </button>
          </div>
          <p>
            If this keeps happening, email{' '}
            <a href={LINKS.CONTACT}>tech@anikalegal.org.au</a> - your answers
            are still saved on this device.
          </p>
        </>
      )}
    </div>
  )
}
