import { getRecaptchaSiteKey } from '../config'
import { logException } from '../utils'

// Minimal shape of the global grecaptcha the v3 script installs.
interface Grecaptcha {
  ready: (cb: () => void) => void
  execute: (siteKey: string, opts: { action: string }) => Promise<string>
}

const getGrecaptcha = (): Grecaptcha | undefined =>
  (window as unknown as { grecaptcha?: Grecaptcha }).grecaptcha

// Load the reCAPTCHA v3 script once (single in-flight promise), resolving the
// ready grecaptcha object, or null when there is no site key or it fails.
let loadPromise: Promise<Grecaptcha | null> | null = null

const loadScript = (siteKey: string): Promise<Grecaptcha | null> =>
  new Promise((resolve) => {
    const existing = getGrecaptcha()
    if (existing) {
      existing.ready(() => resolve(existing))
      return
    }
    const script = document.createElement('script')
    script.src = `https://www.google.com/recaptcha/api.js?render=${encodeURIComponent(
      siteKey
    )}`
    script.async = true
    script.onload = () => {
      const grecaptcha = getGrecaptcha()
      if (grecaptcha) grecaptcha.ready(() => resolve(grecaptcha))
      else resolve(null)
    }
    script.onerror = () => resolve(null)
    document.head.appendChild(script)
  })

const loadRecaptcha = (): Promise<Grecaptcha | null> => {
  if (loadPromise) return loadPromise
  const siteKey = getRecaptchaSiteKey()
  if (!siteKey) {
    loadPromise = Promise.resolve(null)
    return loadPromise
  }
  loadPromise = loadScript(siteKey).catch((error) => {
    logException(error)
    return null
  })
  return loadPromise
}

/**
 * A reCAPTCHA v3 token for the given action, or "" when reCAPTCHA is
 * unavailable (no site key or load failure). The server rejects a missing
 * token, so the caller surfaces that as a normal submission error.
 */
export const getRecaptchaToken = async (action: string): Promise<string> => {
  const grecaptcha = await loadRecaptcha()
  const siteKey = getRecaptchaSiteKey()
  if (!grecaptcha || !siteKey) return ''
  try {
    return await grecaptcha.execute(siteKey, { action })
  } catch (error) {
    logException(error)
    return ''
  }
}
