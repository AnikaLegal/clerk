import { Model } from 'survey-core'

import { getGoogleMapsApiKey, isMockMaps } from '../../config'
import { logException } from '../../utils'
import { loadPlaces } from './load-maps'
import { isVictoria, parseAddressComponents } from './parse'
import type { AddressComponentLike } from './parse'

// Question names in the home-address block (see questions/property.ts).
const SEARCH = 'ADDRESS_SEARCH'
const ADDRESS = 'ADDRESS'
const SUBURB = 'SUBURB'
const POSTCODE = 'POSTCODE'

// Bare survey.data key (not a question, so never serialized) that records
// whether address search is available. The address questions' visibleIf /
// enableIf / requiredIf expressions key off it: unset or false means plain
// manual entry (three editable, required fields and no search box).
const MAPS_AVAILABLE = 'MAPS_AVAILABLE'

// Rough bounding box of Victoria, to restrict autocomplete suggestions. A
// bordering address can still slip through, so selections are validated with
// isVictoria as well.
export const VIC_BOUNDS = {
  west: 140.8,
  south: -39.3,
  east: 150.1,
  north: -33.9,
}

const NON_VIC_MESSAGE =
  'Sorry, we can only help renters in Victoria. Please choose a Victorian address.'

const DEBOUNCE_MS = 300
const MIN_CHARS = 3

// Structural types for the slice of the Places Autocomplete Data API we use
// (google.maps.places.AutocompleteSuggestion et al). The mock installs
// API-compatible fakes, so everything below the fetch call is shared.
interface PredictionLike {
  text: unknown
  toPlace: () => {
    fetchFields?: (options: { fields: string[] }) => Promise<unknown>
    addressComponents?: AddressComponentLike[]
  }
}

interface SuggestionLike {
  placePrediction: PredictionLike | null
}

interface PlacesNamespace {
  AutocompleteSessionToken: new () => object
  AutocompleteSuggestion: {
    fetchAutocompleteSuggestions: (request: {
      input: string
      sessionToken: object
      includedRegionCodes: string[]
      locationRestriction: typeof VIC_BOUNDS
    }) => Promise<{ suggestions: SuggestionLike[] }>
  }
}

const placesApi = (): PlacesNamespace | null => {
  const globals = window as unknown as {
    google?: { maps?: { places?: PlacesNamespace } }
  }
  return globals.google?.maps?.places ?? null
}

// The prediction's display text: FormattableText carries the string on .text.
const predictionLabel = (prediction: PredictionLike): string => {
  const text = prediction.text as { text?: string } | string | null
  if (typeof text === 'string') return text
  return text?.text ?? String(text ?? '')
}

/**
 * Wire Google Places address autocomplete onto the ADDRESS_SEARCH question's
 * own input, rendered as a WAI-ARIA combobox: a debounced suggestion list fed
 * by the Places Autocomplete Data API, keyboard and mouse selectable. Choosing
 * a Victorian address fills the read-only ADDRESS / SUBURB / POSTCODE fields
 * below the search box; the ADDRESS_MANUAL checkbox (a sibling question)
 * flips those fields editable instead - that toggling is all SurveyJS
 * enableIf / requiredIf expressions, not DOM work done here. Without an API
 * key (dev/CI) or if Maps fails to load, MAPS_AVAILABLE stays false and the
 * form is plain manual entry.
 */
export const attachAddressAutocomplete = (survey: Model) => {
  const enabled = Boolean(getGoogleMapsApiKey()) || isMockMaps()
  survey.setValue(MAPS_AVAILABLE, enabled)
  if (!enabled) return

  // Server-side resume: the parts are stored but the (uiOnly) search text may
  // not be - compose a display value so the search box reflects the address.
  if (survey.getValue(ADDRESS) && !survey.getValue(SEARCH)) {
    const line2 = [survey.getValue(SUBURB), 'VIC', survey.getValue(POSTCODE)]
      .filter(Boolean)
      .join(' ')
    survey.setValue(
      SEARCH,
      [survey.getValue(ADDRESS), line2].filter(Boolean).join(', ')
    )
  }

  void loadPlaces().then((ok) => {
    if (!ok) {
      // Script failed to load: degrade to plain manual entry.
      survey.setValue(MAPS_AVAILABLE, false)
    }
  })

  // One Places session (for billing) spans the keystrokes leading up to a
  // selection; the token renews after each selection.
  let sessionToken: object | null = null
  const getSessionToken = (): object | null => {
    const api = placesApi()
    if (!api) return null
    sessionToken = sessionToken ?? new api.AutocompleteSessionToken()
    return sessionToken
  }

  const clearParts = () => {
    survey.setValue(ADDRESS, undefined)
    survey.setValue(SUBURB, undefined)
    survey.setValue(POSTCODE, undefined)
  }

  survey.onAfterRenderQuestion.add((_, options) => {
    if (options.question.name !== SEARCH) return
    const host = options.htmlElement
    const input = host.querySelector<HTMLInputElement>('input')
    // The page-transition animation remounts the survey view with fresh DOM,
    // so wire each new input once.
    if (!input || input.dataset.combobox) return
    input.dataset.combobox = 'true'

    // -- DOM scaffolding -----------------------------------------------------
    const wrapper = input.parentElement
    if (!wrapper) return
    wrapper.classList.add('intake-combobox')

    const listId = 'intake-address-listbox'
    const list = document.createElement('ul')
    list.id = listId
    list.className = 'intake-combobox__list'
    list.setAttribute('role', 'listbox')
    list.hidden = true
    wrapper.appendChild(list)

    // Errors (the non-Victoria rejection) render through the question's own
    // SurveyJS error box, like any validation message.
    const question = options.question

    input.setAttribute('role', 'combobox')
    input.setAttribute('aria-autocomplete', 'list')
    input.setAttribute('aria-controls', listId)
    input.setAttribute('aria-expanded', 'false')

    // A clear (x) button inside the right edge of the field. Its visibility is
    // pure CSS: hidden while the field is empty (:placeholder-shown - the
    // question defines a placeholder) or read-only (manual mode's enableIf).
    // The icon is an inline SVG cross: it centres geometrically in the button
    // (a text glyph sits on a baseline) and follows the button's text colour.
    const clearButton = document.createElement('button')
    clearButton.type = 'button'
    clearButton.className = 'intake-combobox__clear'
    clearButton.setAttribute('aria-label', 'Clear address search')
    clearButton.innerHTML =
      '<svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true" focusable="false">' +
      '<path d="M6 6 L18 18 M18 6 L6 18" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" fill="none"/>' +
      '</svg>'
    wrapper.appendChild(clearButton)

    // -- listbox state -------------------------------------------------------
    let suggestions: SuggestionLike[] = []
    let activeIndex = -1
    let requestStamp = 0
    let debounceTimer: number | undefined

    const close = () => {
      suggestions = []
      activeIndex = -1
      list.hidden = true
      list.innerHTML = ''
      input.setAttribute('aria-expanded', 'false')
      input.removeAttribute('aria-activedescendant')
    }

    const setActive = (index: number) => {
      activeIndex = index
      const items = list.querySelectorAll('li')
      items.forEach((item, i) => {
        item.classList.toggle('intake-combobox__option--active', i === index)
        item.setAttribute('aria-selected', i === index ? 'true' : 'false')
      })
      if (index >= 0) {
        input.setAttribute('aria-activedescendant', `${listId}-${index}`)
        items[index]?.scrollIntoView({ block: 'nearest' })
      } else {
        input.removeAttribute('aria-activedescendant')
      }
    }

    const render = () => {
      list.innerHTML = ''
      if (!suggestions.length) {
        close()
        return
      }
      suggestions.forEach((suggestion, index) => {
        const prediction = suggestion.placePrediction
        if (!prediction) return
        const item = document.createElement('li')
        item.id = `${listId}-${index}`
        item.className = 'intake-combobox__option'
        item.setAttribute('role', 'option')
        item.setAttribute('aria-selected', 'false')
        item.textContent = predictionLabel(prediction)
        // mousedown (not click) so the selection lands before the input blur.
        item.addEventListener('mousedown', (event) => {
          event.preventDefault()
          void select(prediction)
        })
        list.appendChild(item)
      })
      list.hidden = false
      input.setAttribute('aria-expanded', 'true')
      setActive(-1)
    }

    const select = async (prediction: PredictionLike) => {
      try {
        const place = prediction.toPlace()
        await place.fetchFields?.({ fields: ['addressComponents'] })
        const parsed = parseAddressComponents(place.addressComponents ?? [])
        if (!isVictoria(parsed)) {
          // Show the rejected address in the field (not a previously selected
          // one) so the error reads against what the user picked.
          survey.setValue(SEARCH, predictionLabel(prediction))
          input.value = predictionLabel(prediction)
          question.clearErrors()
          question.addError(NON_VIC_MESSAGE)
          close()
          return
        }
        question.clearErrors()
        survey.setValue(ADDRESS, parsed.address)
        survey.setValue(SUBURB, parsed.suburb)
        const postcode = Number(parsed.postcode)
        survey.setValue(POSTCODE, Number.isFinite(postcode) ? postcode : null)
        // Set both the question value and the DOM input: the question value is
        // what persists, but a focused input repaints from the DOM value.
        survey.setValue(SEARCH, predictionLabel(prediction))
        input.value = predictionLabel(prediction)
        // A selection ends the Places billing session.
        sessionToken = null
        close()
      } catch (error) {
        logException(error)
      }
    }

    const fetchSuggestions = (text: string) => {
      const api = placesApi()
      const token = getSessionToken()
      if (!api || !token) return
      const stamp = ++requestStamp
      api.AutocompleteSuggestion.fetchAutocompleteSuggestions({
        input: text,
        sessionToken: token,
        includedRegionCodes: ['au'],
        locationRestriction: VIC_BOUNDS,
      })
        .then((result) => {
          // Discard stale responses that resolve after a newer keystroke.
          if (stamp !== requestStamp) return
          suggestions = result.suggestions.filter((s) => s.placePrediction)
          render()
        })
        .catch((error) => {
          logException(error)
          close()
        })
    }

    input.addEventListener('input', () => {
      // Keep the question value in step with the typed text (text questions
      // otherwise commit on blur): a re-render mid-typing - e.g. showing the
      // Victoria error - would repaint the input from a stale model value,
      // resurrecting the previously selected address.
      survey.setValue(SEARCH, input.value)
      // Typing invalidates any previously selected address, so the parts (and
      // any Victoria error) reset until a new suggestion is chosen.
      clearParts()
      question.clearErrors()
      window.clearTimeout(debounceTimer)
      const text = input.value.trim()
      if (text.length < MIN_CHARS) {
        close()
        return
      }
      debounceTimer = window.setTimeout(
        () => fetchSuggestions(text),
        DEBOUNCE_MS
      )
    })

    input.addEventListener('keydown', (event) => {
      if (list.hidden) return
      if (event.key === 'ArrowDown') {
        event.preventDefault()
        setActive(activeIndex >= suggestions.length - 1 ? 0 : activeIndex + 1)
      } else if (event.key === 'ArrowUp') {
        event.preventDefault()
        setActive(activeIndex <= 0 ? suggestions.length - 1 : activeIndex - 1)
      } else if (event.key === 'Enter') {
        if (activeIndex >= 0) {
          event.preventDefault()
          const prediction = suggestions[activeIndex]?.placePrediction
          if (prediction) void select(prediction)
        }
      } else if (event.key === 'Escape') {
        event.preventDefault()
        close()
      }
    })

    input.addEventListener('blur', () => {
      window.setTimeout(close, 150)
    })

    clearButton.addEventListener('click', () => {
      // Same effect as the user deleting the text: reset the search, the
      // filled parts and any error, then hand focus back to the field.
      survey.setValue(SEARCH, undefined)
      input.value = ''
      clearParts()
      question.clearErrors()
      close()
      input.focus()
    })
  })
}
