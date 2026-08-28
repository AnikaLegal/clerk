import { LINKS } from '../consts'
import { useAnnouncePage } from '../views/announce'

interface ConfirmProps {
  // Where the resume link would go, or null when there is nowhere to send it
  // - no email answered yet.
  email: string | null
  // Sends the link (where there is an address) and shows the message below.
  onConfirm: () => void
  // Back into the form, unchanged.
  onCancel: () => void
  sending: boolean
}

/**
 * Asked before the user leaves, so "Save & finish later" is a decision rather
 * than a click that swaps the page from under them. It also sets expectations:
 * the answers are already saved, and this is really about how to get back.
 */
export const SaveExitConfirm = ({
  email,
  onConfirm,
  onCancel,
  sending,
}: ConfirmProps) => {
  const headingRef = useAnnouncePage('Finish later?')
  return (
    <>
      <h1 tabIndex={-1} ref={headingRef}>
        Finish later?
      </h1>
      <p>
        Your answers so far are saved.{' '}
        {email ? (
          <>
            We&apos;ll email a link to <strong>{email}</strong> so you can pick
            up where you left off on any device.
          </>
        ) : (
          <>
            Come back to this form in this browser and it will pick up where you
            left off.
          </>
        )}
      </p>
      <div className="intake-message__actions">
        <button
          type="button"
          className="intake-home-link intake-message__resume"
          onClick={onConfirm}
          disabled={sending}
        >
          {sending ? 'Sending...' : email ? 'Email me a link' : 'Finish later'}
        </button>
        <button
          type="button"
          className="intake-home-link intake-message__resume"
          onClick={onCancel}
        >
          Keep going
        </button>
      </div>
    </>
  )
}

interface SavedProps {
  // The address the resume link went to, or null when there was nowhere to
  // send it - no email answered yet, or the send failed.
  emailedTo: string | null
  // Back into the form, for someone who changes their mind.
  onResume: () => void
}

/**
 * Shown once the user has chosen to finish later. Their answers are already
 * saved - on this device on every page, and to the server once an email
 * address is given - so this says where they stand and how to get back.
 */
export const SavedMessage = ({ emailedTo, onResume }: SavedProps) => {
  const headingRef = useAnnouncePage('Your progress is saved')
  return (
    <>
      <h1 tabIndex={-1} ref={headingRef}>
        Your progress is saved
      </h1>
      {emailedTo ? (
        <p>
          We&apos;ve emailed a link to <strong>{emailedTo}</strong>. Open it on
          any device to pick up where you left off.
        </p>
      ) : (
        <p>
          Come back to this form in this browser and it will pick up where you
          left off.
        </p>
      )}
      <p>You can close this tab whenever you like.</p>
      <div className="intake-message__actions">
        <button
          type="button"
          className="intake-home-link intake-message__resume"
          onClick={onResume}
        >
          Keep going
        </button>
        <a className="intake-home-link" href={LINKS.HOME}>
          Go to the Anika Legal home page
        </a>
      </div>
    </>
  )
}
