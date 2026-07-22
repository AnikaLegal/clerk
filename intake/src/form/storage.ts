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
}

// A factory (not a shared constant) so every load returns an independent
// state object - callers can mutate their copy without corrupting later loads.
const emptyState = (): StoredState => ({
  submissionId: null,
  data: {},
  visited: [],
  currentPage: null,
})

export const loadState = (): StoredState => {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return emptyState()
    const parsed = JSON.parse(raw)
    return {
      submissionId: parsed.submissionId ?? null,
      data: parsed.data ?? {},
      visited: Array.isArray(parsed.visited) ? parsed.visited : [],
      currentPage: parsed.currentPage ?? null,
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
