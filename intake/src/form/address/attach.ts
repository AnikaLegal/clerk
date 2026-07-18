import { Model } from 'survey-core'

import { getGoogleMapsApiKey } from '../../config'
import { logException } from '../../utils'
import { loadPlaces } from './load-maps'
import { AddressComponentLike, isVictoria, parseAddressComponents } from './parse'

// Field names on the PROPERTY_ADDRESS page.
const ADDRESS = 'ADDRESS'
const SUBURB = 'SUBURB'
const POSTCODE = 'POSTCODE'

// Helper value (not a real question, so serializeAnswers never sends it) that
// records whether the user is using the address search box or typing the
// fields manually. Persisted in survey.data so it survives a reload.
const MODE = 'ADDRESS_MODE'
type Mode = 'search' | 'manual'

// Rough bounding box of Victoria, to restrict autocomplete suggestions. A
// bordering address can still slip through, so selections are validated with
// isVictoria as well.
const VIC_BOUNDS = { west: 140.8, south: -39.3, east: 150.1, north: -33.9 }

const MANUAL_LINK = 'Enter address manually'
const SEARCH_LINK = 'Search for my address instead'
const NON_VIC_MESSAGE =
  'Sorry, we can only help renters in Victoria. Please choose a Victorian address, or enter it manually.'

// Minimal shape of the gmp-select event / selected place we use. The ambient
// google types cover these, but casting through these keeps the handler robust
// across Maps API versions (which we cannot exercise without a live key).
interface SelectEvent {
  placePrediction?: {
    toPlace: () => {
      fetchFields?: (options: { fields: string[] }) => Promise<unknown>
      addressComponents?: AddressComponentLike[]
    }
  }
}

const modeOf = (survey: Model): Mode =>
  survey.getValue(MODE) === 'manual' ? 'manual' : 'search'

const makeElement = (
  tag: string,
  className: string,
  text?: string
): HTMLElement => {
  const node = document.createElement(tag)
  node.className = className
  if (text !== undefined) node.textContent = text
  return node
}

const makeLink = (text: string, onClick: () => void): HTMLElement => {
  const link = makeElement('button', 'intake-address__toggle', text)
  ;(link as HTMLButtonElement).type = 'button'
  link.addEventListener('click', onClick)
  return link
}

/**
 * Wire Google Places address autocomplete into the intake form's ADDRESS
 * question. In "search" mode a single search box replaces the street/suburb/
 * postcode inputs and fills them on selection; a toggle switches to "manual"
 * mode, which reveals the three editable fields. Without an API key (dev/CI) or
 * if Maps fails to load, the form stays in manual mode. Mirrors the "attach a
 * handler to the survey Model" pattern in upload-handler.ts.
 */
export const attachAddressAutocomplete = (survey: Model) => {
  const hasKey = Boolean(getGoogleMapsApiKey())
  if (!hasKey) {
    // No search box available: always manual, even if a stored session left the
    // mode on 'search' (e.g. the key was removed, or a server-side resume).
    survey.setValue(MODE, 'manual')
  } else if (!survey.getValue(MODE)) {
    survey.setValue(MODE, 'search')
  }

  // Latest rendered host element for each field, refreshed on every render
  // (the page-transition animation remounts the survey view). applyMode reads
  // these to show/hide the right pieces for the current mode.
  const hosts: {
    address?: HTMLElement
    suburb?: HTMLElement
    postcode?: HTMLElement
  } = {}

  const setMode = (mode: Mode) => {
    survey.setValue(MODE, mode)
    applyMode()
  }

  const applyMode = () => {
    const search = modeOf(survey) === 'search'
    // Hide the suburb + postcode rows in search mode (they are still SurveyJS-
    // visible, so serializeAnswers keeps them; only the DOM is hidden).
    if (hosts.suburb) hosts.suburb.style.display = search ? 'none' : ''
    if (hosts.postcode) hosts.postcode.style.display = search ? 'none' : ''
    const host = hosts.address
    if (!host) return
    // Hide the native street input in search mode; show the search box.
    const input = host.querySelector<HTMLElement>('input')
    if (input) input.style.display = search ? 'none' : ''
    const box = host.querySelector<HTMLElement>('.intake-address__search')
    if (box) box.style.display = search ? '' : 'none'
    const manualLink = host.querySelector<HTMLElement>(
      '.intake-address__toggle--manual'
    )
    if (manualLink) manualLink.style.display = search ? '' : 'none'
    const searchLink = host.querySelector<HTMLElement>(
      '.intake-address__toggle--search'
    )
    if (searchLink) searchLink.style.display = search ? 'none' : ''
  }

  const onSelect = (status: HTMLElement) => async (event: SelectEvent) => {
    try {
      const place = event.placePrediction?.toPlace()
      if (!place) return
      // Only the address components are used (see parseAddressComponents), so
      // request just those to keep the Places billing to a single field.
      await place.fetchFields?.({ fields: ['addressComponents'] })
      const parsed = parseAddressComponents(place.addressComponents ?? [])
      if (!isVictoria(parsed)) {
        status.textContent = NON_VIC_MESSAGE
        status.className = 'intake-address__status intake-address__status--error'
        return
      }
      survey.setValue(ADDRESS, parsed.address)
      survey.setValue(SUBURB, parsed.suburb)
      const postcode = Number(parsed.postcode)
      survey.setValue(POSTCODE, Number.isFinite(postcode) ? postcode : null)
      status.textContent = [
        parsed.address,
        [parsed.suburb, 'VIC', parsed.postcode].filter(Boolean).join(' '),
      ]
        .filter(Boolean)
        .join(', ')
      status.className = 'intake-address__status intake-address__status--ok'
    } catch (error) {
      logException(error)
    }
  }

  // Build the search box (Google element + status line) inside the ADDRESS
  // question once, then mount the Places element when the library has loaded.
  const buildSearchBox = (host: HTMLElement) => {
    const content = host.querySelector<HTMLElement>('.sd-question__content')
    if (!content) return
    const box = makeElement('div', 'intake-address__search')
    const status = makeElement('p', 'intake-address__status')
    box.appendChild(status)
    content.appendChild(box)

    void loadPlaces().then((ok) => {
      if (!ok) {
        // No key or load failure: manual entry is the only option.
        setMode('manual')
        return
      }
      try {
        const element = new google.maps.places.PlaceAutocompleteElement({
          includedRegionCodes: ['au'],
          locationRestriction: VIC_BOUNDS,
        })
        element.className = 'intake-address__input'
        box.insertBefore(element, status)
        element.addEventListener(
          'gmp-select',
          (event) => void onSelect(status)(event as unknown as SelectEvent)
        )
      } catch (error) {
        logException(error)
        setMode('manual')
      }
    })
  }

  const enhanceAddress = (host: HTMLElement) => {
    hosts.address = host
    if (host.dataset.addressEnhanced) {
      applyMode()
      return
    }
    host.dataset.addressEnhanced = 'true'
    // Without a key there is no search box, so the form stays purely manual and
    // no search/manual toggles are offered (mode is forced to manual above).
    if (getGoogleMapsApiKey()) {
      const content = host.querySelector<HTMLElement>('.sd-question__content')
      if (content) {
        const manual = makeLink(MANUAL_LINK, () => setMode('manual'))
        manual.classList.add('intake-address__toggle--manual')
        const search = makeLink(SEARCH_LINK, () => setMode('search'))
        search.classList.add('intake-address__toggle--search')
        content.appendChild(manual)
        content.appendChild(search)
      }
      buildSearchBox(host)
    }
    applyMode()
  }

  survey.onAfterRenderQuestion.add((_, options) => {
    const name = options.question.name
    if (name === ADDRESS) {
      enhanceAddress(options.htmlElement)
    } else if (name === SUBURB) {
      hosts.suburb = options.htmlElement
      applyMode()
    } else if (name === POSTCODE) {
      hosts.postcode = options.htmlElement
      applyMode()
    }
  })
}
