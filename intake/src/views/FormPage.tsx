import { useCallback, useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Survey } from 'survey-react-ui'

import { events } from '../analytics'
import { ApiError } from '../api/client'
import { SectionProgress } from '../comps/SectionProgress'
import { ROUTES } from '../consts'
import { resetFunnel } from '../form/funnel'
import { WELCOME_PAGE } from '../form/model'
import { serializeAnswers } from '../form/serialize'
import { setUpForm } from '../form/setup'
import { clearState } from '../form/storage'
import { useFormNavigation } from '../form/useFormNavigation'
import { logException } from '../utils'
import { setDocumentTitle } from './announce'
import { SubmitState, SubmitStatus } from './SubmitStatus'

export const FormPage = () => {
  const navigate = useNavigate()
  const { survey, saver, visited, session } = useMemo(setUpForm, [])

  // Post-submit state, rendered as our own splash (see SubmitStatus) instead of
  // SurveyJS's completed page / save-data banner, so both errors match the rest
  // of the intake flow and the unrecoverable case can drop the retry button.
  // null while filling the form; a successful submit navigates to SubmittedPage.
  const [submitState, setSubmitState] = useState<SubmitState | null>(null)

  const attemptSubmit = useCallback(() => {
    setSubmitState('submitting')
    const answers = serializeAnswers(survey, visited)
    saver
      .submit(answers)
      .then(() => {
        // Guard the analytics call: a throwing gtag/fbq (e.g. clobbered by a
        // privacy extension) must not land in .catch and show the submit-error
        // screen for a submission the server already accepted - which would
        // also loop, since the retry re-runs this same throwing call.
        try {
          events.onFormComplete()
        } catch (error) {
          logException(error)
        }
        clearState()
        resetFunnel()
        navigate(ROUTES.SUBMITTED)
      })
      .catch((error) => {
        logException(error)
        const status = (error as ApiError)?.status
        // A 4xx is not transient (e.g. a missing-CSRF 403 or a validation 400):
        // retrying just loops on the same failure, so offer no retry and point
        // the user to a person. Network errors and 5xx are worth retrying.
        const permanent =
          typeof status === 'number' && status >= 400 && status < 500
        setSubmitState(permanent ? 'permanent' : 'transient')
      })
  }, [survey, saver, visited, navigate])

  // Drive the survey's page lifecycle (history sync, funnel, exits, persistence)
  // and read back the progress-indicator state plus the jump-to-section wiring.
  const { progress, navigable, jumpToSection } = useFormNavigation({
    survey,
    saver,
    visited,
    session,
    attemptSubmit,
  })

  // Restore the form's title after a splash view (e.g. Go back from an exit
  // page) changed it. Matches the title the Django shell renders on load.
  // Focus is handled by the survey itself (autoFocusFirstQuestion).
  useEffect(() => {
    setDocumentTitle('Get free help')
  }, [])

  // Once the form is submitting or has failed, replace the survey with the
  // post-submit splash (a successful submit navigates away before this shows).
  if (submitState) {
    return (
      <div className="intake-form">
        <SubmitStatus state={submitState} onRetry={attemptSubmit} />
      </div>
    )
  }

  return (
    <div
      className={
        progress.name === WELCOME_PAGE
          ? 'intake-form intake-form--welcome'
          : 'intake-form'
      }
    >
      {progress.section >= 0 && (
        <SectionProgress
          current={progress.section}
          page={progress.page}
          pageCount={progress.pageCount}
          navigable={navigable}
          onJump={jumpToSection}
        />
      )}
      {/* The outer div clips the horizontal slide; the inner is re-keyed by page
          name so the direction-aware animation in global.css replays on every
          page change. The survey Model is stable across the remount (it lives in
          useMemo), so only the view is rebuilt. */}
      <div className="intake-page">
        <div
          key={progress.name}
          className={`intake-page__inner intake-page__inner--${progress.direction}`}
        >
          <Survey model={survey} />
        </div>
      </div>
    </div>
  )
}
