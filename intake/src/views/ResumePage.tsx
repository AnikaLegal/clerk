import { useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'

import { api } from '../api'
import { ROUTES } from '../consts'
import { deserializeAnswers } from '../form/serialize'
import { saveState } from '../form/storage'
import { logException } from '../utils'

/**
 * Restore a partial submission from the server and continue the form.
 * Linked from MailChimp abandonment reminder emails as /resume/?sub=<id>.
 */
export const ResumePage = () => {
  const navigate = useNavigate()
  const [params] = useSearchParams()

  useEffect(() => {
    const submissionId = params.get('sub')
    if (!submissionId) {
      navigate(ROUTES.LANDING, { replace: true })
      return
    }
    api.submission
      .get(submissionId)
      .then((submission) => {
        saveState({
          submissionId: submission.id,
          data: deserializeAnswers(submission.answers),
          // Keys present on the wire are exactly the questions the user
          // passed; the form resumes at the first unanswered one.
          visited: Object.keys(submission.answers),
          currentPage: null,
        })
        navigate(ROUTES.FORM, { replace: true })
      })
      .catch((error) => {
        // 403 (already submitted) or 404 - start from scratch.
        logException(error)
        navigate(ROUTES.LANDING, { replace: true })
      })
    // Deliberately run once on mount.
  }, [])

  return (
    <div className="intake-splash">
      <p>Loading your saved answers...</p>
    </div>
  )
}
