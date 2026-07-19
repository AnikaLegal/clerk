import { getGoogleMapsApiKey, isMockMaps } from '../../config'
import { logException } from '../../utils'

// Loads the Google Maps JS "places" library exactly once (a single in-flight
// promise), resolving true on success and false when there is no API key or the
// script fails to load. On false the address section falls back to manual entry.
let loadPromise: Promise<boolean> | null = null

// Name of the global the Maps script calls once it has loaded.
const CALLBACK = '__intakeInitMaps'

const injectScript = (key: string): Promise<boolean> =>
  new Promise((resolve) => {
    const globals = window as unknown as Record<string, unknown>
    globals[CALLBACK] = () => resolve(true)
    const params = new URLSearchParams({
      key,
      v: 'weekly',
      libraries: 'places',
      loading: 'async',
      callback: CALLBACK,
    })
    const script = document.createElement('script')
    script.src = `https://maps.googleapis.com/maps/api/js?${params.toString()}`
    script.async = true
    script.onerror = () => resolve(false)
    document.head.appendChild(script)
  })

export const loadPlaces = (): Promise<boolean> => {
  if (loadPromise) return loadPromise
  if (isMockMaps()) {
    // Dev preview: install the fake Places backend instead of loading Google.
    // The dynamic import keeps the mock out of the production bundle.
    loadPromise = import('./mock').then(({ installMockPlaces }) => {
      installMockPlaces()
      return true
    })
    return loadPromise
  }
  const key = getGoogleMapsApiKey()
  if (!key) {
    loadPromise = Promise.resolve(false)
    return loadPromise
  }
  loadPromise = injectScript(key).catch((error) => {
    logException(error)
    return false
  })
  return loadPromise
}
