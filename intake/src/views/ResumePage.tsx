import { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'

import { api } from '../api'
import { LINKS, ROUTES } from '../consts'
import { classifyResumeError, shouldKeepLocalState } from '../form/resume'
import { deserializeAnswers } from '../form/serialize'
import { loadState, saveState } from '../form/storage'
import { logException } from '../utils'
import { useAnnouncePage } from './announce'

type Status = 'loading' | 'error' | 'already-submitted'

/**
 * Restore a partial submission from the server and continue the form.
 * Linked from MailChimp abandonment reminder emails as /resume/?sub=<id>.
 * The server snapshot only wins when it is the fresher copy (see
 * shouldKeepLocalState); failures are surfaced rather than silently starting
 * a fresh form, which would invite duplicate submissions.
 */
export const ResumePage = () => {
  const navigate = useNavigate()
  const [params] = useSearchParams()
  const [status, setStatus] = useState<Status>('loading')
  const [attempt, setAttempt] = useState(0)
  const headingRef = useAnnouncePage(
    status === 'error'
      ? "We couldn't load your saved answers"
      : status === 'already-submitted'
        ? 'This application has already been submitted'
        : ''
  )

  useEffect(() => {
    const submissionId = params.get('sub')
    if (!submissionId) {
      navigate(ROUTES.LANDING, { replace: true })
      return
    }
    let cancelled = false
    api.submission
      .get(submissionId)
      .then((submission) => {
        if (cancelled) return
        // Keep the browser's own copy when it is the same submission with at
        // least as much progress - it saves on every page change, while the
        // server copy lags behind the debounced PATCHes.
        if (
          !shouldKeepLocalState(loadState(), submissionId, submission.answers)
        ) {
          saveState({
            submissionId: submission.id,
            data: deserializeAnswers(submission.answers),
            // Keys present on the wire are exactly the questions the user
            // passed; the form resumes at the first unanswered one.
            visited: Object.keys(submission.answers),
            currentPage: null,
          })
        }
        navigate(ROUTES.LANDING, { replace: true })
      })
      .catch((error) => {
        if (cancelled) return
        logException(error)
        const failure = classifyResumeError(error)
        if (failure === 'not-found') {
          // A genuinely dead link - start from scratch.
          navigate(ROUTES.LANDING, { replace: true })
          return
        }
        setStatus(failure)
      })
    return () => {
      cancelled = true
    }
    // Re-runs when the user presses Try again (attempt changes).
  }, [params, navigate, attempt])

  if (status === 'already-submitted') {
    return (
      <div className="intake-splash">
        <h1 tabIndex={-1} ref={headingRef}>
          This application has already been submitted
        </h1>
        <p>
          We&apos;ve got your answers and our paralegals will contact you soon
          to discuss how we can help you.
        </p>
        <div className="intake-button-group">
          <a href={LINKS.HOME} className="d-btn d-btn-primary">
            Return home
          </a>
        </div>
      </div>
    )
  }

  if (status === 'error') {
    return (
      <div className="intake-splash">
        <h1 tabIndex={-1} ref={headingRef}>
          Sorry, we couldn&apos;t load your saved answers
        </h1>
        <p>
          Something went wrong on the way to our server. Please try again - if
          it keeps happening, you can start a new application instead.
        </p>
        <div className="intake-button-group">
          <button
            type="button"
            className="d-btn d-btn-primary"
            onClick={() => {
              setStatus('loading')
              setAttempt((n) => n + 1)
            }}
          >
            Try again
          </button>
          <button
            type="button"
            className="d-btn intake-btn-secondary"
            onClick={() => navigate(ROUTES.LANDING, { replace: true })}
          >
            Start a new application
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="intake-splash">
      <p>Loading your saved answers...</p>
    </div>
  )
}
