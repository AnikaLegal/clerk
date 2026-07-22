import { api } from '../api'
import { isAlreadySubmitted } from '../api/errors'
import { logException } from '../utils'
import { Answers } from './types'

const PATCH_DEBOUNCE_MS = 1500

/**
 * Manages the submission lifecycle against the backend: create once (at the
 * EMAIL step), debounced single-flight PATCHes as the user progresses, and
 * an awaited flush + submit at the end. This fixes the old form's bug where
 * the created submission's id was lost and a duplicate was created at
 * final submit.
 */
export class SubmissionSaver {
  submissionId: string | null = null
  private onIdChange: (id: string) => void
  private createInFlight: Promise<void> | null = null
  private patchInFlight: Promise<void> | null = null
  private pendingAnswers: Answers | null = null
  private debounceTimer: ReturnType<typeof setTimeout> | null = null

  constructor(submissionId: string | null, onIdChange: (id: string) => void) {
    this.submissionId = submissionId
    this.onIdChange = onIdChange
  }

  // Create the submission once. Non-blocking for navigation; PATCHes are
  // no-ops until it resolves.
  create(answers: Answers): Promise<void> {
    if (this.submissionId) return Promise.resolve()
    if (this.createInFlight) return this.createInFlight
    this.createInFlight = api.submission
      .create(answers)
      .then((submission) => {
        this.submissionId = submission.id
        this.onIdChange(submission.id)
      })
      .finally(() => {
        this.createInFlight = null
      })
    return this.createInFlight
  }

  // Debounced, latest-wins, one PATCH in flight at a time. Failures are
  // logged and retried on the next page change (like the old form).
  schedulePatch(answers: Answers) {
    this.pendingAnswers = answers
    if (this.debounceTimer) clearTimeout(this.debounceTimer)
    this.debounceTimer = setTimeout(() => this.runPatch(), PATCH_DEBOUNCE_MS)
  }

  // Send any pending snapshot immediately: cancel the debounce and start the
  // PATCH now. Used when waiting is no longer safe - an eligibility exit (the
  // blocked page change means the normal PATCH never fires) and the tab being
  // closed or hidden. Single-flight still applies, and it is a no-op before
  // the submission exists or when nothing is pending.
  flush() {
    if (this.debounceTimer) {
      clearTimeout(this.debounceTimer)
      this.debounceTimer = null
    }
    this.runPatch()
  }

  private runPatch() {
    if (!this.submissionId || this.patchInFlight || !this.pendingAnswers) {
      return
    }
    const answers = this.pendingAnswers
    this.pendingAnswers = null
    this.patchInFlight = api.submission
      .update(this.submissionId, answers)
      .then(() => undefined)
      .catch(logException)
      .finally(() => {
        this.patchInFlight = null
        // A newer snapshot may have arrived while this one was in flight.
        if (this.pendingAnswers) this.runPatch()
      })
  }

  // Final save: cancel the debounce, wait out any in-flight create/PATCH,
  // then save the definitive answers and mark the submission complete. If
  // the create somehow never succeeded, fall back to create-then-submit.
  async submit(answers: Answers): Promise<void> {
    if (this.debounceTimer) clearTimeout(this.debounceTimer)
    this.pendingAnswers = null
    if (this.createInFlight) {
      // A slow EMAIL-time create is still pending: wait for it rather than
      // creating a duplicate submission. If it failed, fall through to the
      // create below.
      await this.createInFlight.catch(() => undefined)
    }
    if (this.patchInFlight) {
      await this.patchInFlight
    }
    try {
      if (this.submissionId) {
        await api.submission.update(this.submissionId, answers)
      } else {
        const submission = await api.submission.create(answers)
        this.submissionId = submission.id
        this.onIdChange(submission.id)
      }
      await api.submission.submit(this.submissionId)
    } catch (error) {
      // A prior submit may have reached the server even though we never saw
      // the response (e.g. a network blip before the retry). The backend
      // then 403s any further writes - that is a success, not a failure.
      if (isAlreadySubmitted(error)) return
      throw error
    }
  }
}
