import { isAlreadySubmitted, isNotFound } from '../api/errors'
import { StoredState } from './storage'
import { Answers } from './types'

/**
 * True when the browser's saved state is the same submission with at least as
 * much progress as the server snapshot. Local state is written on every page
 * change while the server only receives debounced PATCHes (whose failures are
 * retried later), so on the same device the local copy is usually the fresher
 * of the two - overwriting it with the server snapshot would lose answers.
 * Progress is compared as local visited questions vs server answer keys (the
 * server-side equivalent: resume seeds visited from the answer keys).
 */
export const shouldKeepLocalState = (
  local: StoredState,
  submissionId: string,
  serverAnswers: Answers
): boolean =>
  local.submissionId === submissionId &&
  local.visited.length >= Object.keys(serverAnswers).length

export type ResumeFailure = 'already-submitted' | 'not-found' | 'error'

// How a failed resume fetch should be handled: a genuine 404 silently starts
// a fresh form (the link is dead); everything else gets told to the user -
// an already-submitted notice, or a retryable error for network/server
// failures (which would otherwise invite a duplicate submission).
export const classifyResumeError = (error: unknown): ResumeFailure => {
  if (isNotFound(error)) return 'not-found'
  if (isAlreadySubmitted(error)) return 'already-submitted'
  return 'error'
}
