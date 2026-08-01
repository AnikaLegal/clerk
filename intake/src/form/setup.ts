import { Model } from 'survey-core'

import { attachAddressAutocomplete } from './address/attach'
import { buildSurveyModel, WELCOME_PAGE } from './model'
import { restorePosition } from './restore'
import { SubmissionSaver } from './save'
import { loadState, saveState } from './storage'
import { attachUploadHandler } from './upload-handler'

export interface FormState {
  survey: Model
  saver: SubmissionSaver
  visited: Set<string>
  // Id for this form-filling session, stamped into history entries (see the
  // reconcile effect in useFormNavigation).
  session: string
}

// Snapshot the current position + answers to localStorage, so a reload or an
// exit / no-email round trip resumes where the user left off.
export const persistState = (
  survey: Model,
  saver: SubmissionSaver,
  visited: Set<string>,
  session: string
) => {
  saveState({
    submissionId: saver.submissionId,
    data: survey.data,
    visited: [...visited],
    currentPage: survey.currentPage?.name ?? null,
    session,
  })
}

// Build the survey model and its companions (saver, visited set, session) from
// any stored state, restoring a returning user to where they left off. Called
// once per mount via useMemo.
export const setUpForm = (): FormState => {
  const stored = loadState()
  const survey = buildSurveyModel()
  const visited = new Set(stored.visited)
  survey.data = stored.data
  attachUploadHandler(survey)
  attachAddressAutocomplete(survey)

  // Carry the stored session across remounts (exit / no-email round trips,
  // reloads); mint a fresh one when there is no state (a new visitor, or Back
  // after a submit cleared it) so leftover history entries from the previous
  // session are recognised as stale.
  const session = stored.session ?? crypto.randomUUID()

  const saver = new SubmissionSaver(stored.submissionId, () =>
    persistState(survey, saver, visited, session)
  )

  // Restore where the returning user re-enters the form (see restorePosition).
  restorePosition(survey, visited, stored.currentPage)

  // The WELCOME page's forward button reads "Let's get started"; every other
  // page uses "Continue". Set it before the first render (syncPage maintains
  // it on later page changes) so a fresh visitor never sees the wrong label
  // flash.
  survey.pageNextText =
    survey.currentPage?.name === WELCOME_PAGE ? "Let's get started" : 'Continue'

  return { survey, saver, visited, session }
}
