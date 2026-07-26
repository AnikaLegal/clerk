import { STORAGE_KEY } from '../consts'
import { Answers } from './types'

export interface StoredState {
  submissionId: string | null
  // survey.data (upload values in their SurveyJS shape).
  data: Answers
  // Question names the user has passed via Next. Distinguishes "skipped"
  // (null on the wire) from "never reached" (absent on the wire).
  visited: string[]
  // Name of the page the user is on, so the form reopens where they left off.
  currentPage: string | null
  // Id for this form-filling session, stamped into each browser history entry
  // so the history-reconcile effect can ignore leftover entries from an
  // earlier session (e.g. Back after a submit that cleared the state). Null
  // until setUpForm assigns one.
  session: string | null
}

// A factory (not a shared constant) so every load returns an independent
// state object - callers can mutate their copy without corrupting later loads.
const emptyState = (): StoredState => ({
  submissionId: null,
  data: {},
  visited: [],
  currentPage: null,
  session: null,
})

export const loadState = (): StoredState => {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return emptyState()
    const parsed = JSON.parse(raw)
    // Type-check every field, not just parse: a parseable-but-wrong-shaped
    // value (a stale/future schema, hand-edited storage) must degrade to the
    // empty default rather than flow through. A junk submissionId is the worst
    // case - the saver would treat any truthy id as real, 404 every PATCH, and
    // wedge the final submit in a retry loop (clearState only runs on success).
    const isRecord = (v: unknown): v is Answers =>
      typeof v === 'object' && v !== null && !Array.isArray(v)
    return {
      submissionId:
        typeof parsed.submissionId === 'string' ? parsed.submissionId : null,
      data: isRecord(parsed.data) ? parsed.data : {},
      visited: Array.isArray(parsed.visited)
        ? parsed.visited.filter((v: unknown): v is string => typeof v === 'string')
        : [],
      currentPage:
        typeof parsed.currentPage === 'string' ? parsed.currentPage : null,
      session: typeof parsed.session === 'string' ? parsed.session : null,
    }
  } catch {
    return emptyState()
  }
}

export const saveState = (state: StoredState) => {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state))
  } catch {
    // Storage full or unavailable - the form still works within the session.
  }
}

export const clearState = () => {
  try {
    localStorage.removeItem(STORAGE_KEY)
  } catch {
    // Ignore.
  }
}
