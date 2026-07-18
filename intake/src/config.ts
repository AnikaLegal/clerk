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
