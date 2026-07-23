// Dedupe state for the analytics funnel (form_begin / form_step), kept in
// sessionStorage. The events fire the first time the user begins the form or
// reaches each page, but FormPage remounts on every exit-page round trip,
// no-email round trip and reload - and its per-mount refs used to reset each
// time, re-firing events for pages already counted and inflating the funnel.
// sessionStorage survives those remounts within a browsing session and resets
// for a genuinely new session (a fresh tab, e.g. a cross-device resume link).
import { FUNNEL_KEY } from '../consts'

interface FunnelState {
  begun: boolean
  steps: string[]
}

const read = (): FunnelState => {
  try {
    const raw = sessionStorage.getItem(FUNNEL_KEY)
    if (!raw) return { begun: false, steps: [] }
    const parsed = JSON.parse(raw)
    return {
      begun: parsed.begun === true,
      steps: Array.isArray(parsed.steps) ? parsed.steps : [],
    }
  } catch {
    return { begun: false, steps: [] }
  }
}

const write = (state: FunnelState) => {
  try {
    sessionStorage.setItem(FUNNEL_KEY, JSON.stringify(state))
  } catch {
    // sessionStorage unavailable (e.g. storage disabled): events may re-fire
    // on remount, which is no worse than the original behaviour.
  }
}

// True the first time it is called for a page name this session, false
// thereafter - so form_step is reported once per page.
export const markStepReported = (name: string): boolean => {
  const state = read()
  if (state.steps.includes(name)) return false
  state.steps.push(name)
  write(state)
  return true
}

// True the first time it is called this session, false thereafter - so
// form_begin is reported once.
export const markFormBegun = (): boolean => {
  const state = read()
  if (state.begun) return false
  write({ ...state, begun: true })
  return true
}

// Clear the funnel dedupe so a fresh form in the same tab starts a new funnel
// (called on submit, alongside clearState).
export const resetFunnel = () => {
  try {
    sessionStorage.removeItem(FUNNEL_KEY)
  } catch {
    // Ignore.
  }
}
