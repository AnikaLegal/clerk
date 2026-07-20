// Runtime config injected by the Django intake template (base.html) as a
// window global, mirroring window.SENTRY_CONTEXT (see utils.ts). Values come
// from settings via app/intake/utils.py.
interface IntakeConfig {
  googleMapsApiKey: string
  recaptchaSiteKey: string
}

const getConfig = (): Partial<IntakeConfig> =>
  (window as { INTAKE_CONFIG?: IntakeConfig }).INTAKE_CONFIG ?? {}

// Treat the "None" that settings produce for an unset env var as absent.
const cleanKey = (value: string | undefined): string =>
  !value || value === 'None' ? '' : value

// The Google Maps browser key for address autocomplete, or "" when unset
// (dev/CI), in which case the address section falls back to manual entry.
export const getGoogleMapsApiKey = (): string =>
  cleanKey(getConfig().googleMapsApiKey)

// The reCAPTCHA v3 site key guarding the no-email contact form, or "" when
// unset (dev/CI).
export const getRecaptchaSiteKey = (): string =>
  cleanKey(getConfig().recaptchaSiteKey)

// Dev-only preview: with ?mock-maps in the URL a fake Google Places backend
// stands in for the real API, so the address autocomplete can be tried without
// provisioning a key. Captured once at load (before client-side navigation can
// strip the query) and gated on import.meta.env.DEV so it is impossible to
// activate in a production build.
const MOCK_MAPS =
  import.meta.env.DEV &&
  new URLSearchParams(window.location.search).has('mock-maps')

export const isMockMaps = (): boolean => MOCK_MAPS
