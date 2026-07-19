// Runtime config injected by the Django intake template (base.html) as a
// window global, mirroring window.SENTRY_CONTEXT (see utils.ts). Values come
// from settings via app/intake/utils.py.
interface IntakeConfig {
  googleMapsApiKey: string
}

const getConfig = (): Partial<IntakeConfig> =>
  (window as { INTAKE_CONFIG?: IntakeConfig }).INTAKE_CONFIG ?? {}

// The Google Maps browser key for address autocomplete, or "" when unset
// (dev/CI), in which case the address section falls back to manual entry.
export const getGoogleMapsApiKey = (): string =>
  getConfig().googleMapsApiKey ?? ''

// Dev-only preview: with ?mock-maps in the URL a fake Google Places backend
// stands in for the real API, so the address autocomplete can be tried without
// provisioning a key. Captured once at load (before client-side navigation can
// strip the query) and gated on import.meta.env.DEV so it is impossible to
// activate in a production build.
const MOCK_MAPS =
  import.meta.env.DEV &&
  new URLSearchParams(window.location.search).has('mock-maps')

export const isMockMaps = (): boolean => MOCK_MAPS
