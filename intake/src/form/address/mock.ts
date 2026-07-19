// A fake Google Places Autocomplete Data API for previewing the address
// autocomplete without a real API key. Only ever loaded when
// config.isMockMaps() is true (dev-only, ?mock-maps), via a dynamic import so
// none of this ships in the prod bundle. It installs API-compatible stand-ins
// for google.maps.places.AutocompleteSuggestion / AutocompleteSessionToken
// that suggest from a small hardcoded list, so the entire real combobox path
// (fetch -> render -> select -> toPlace -> fetchFields -> parse -> Victoria
// check -> fill) runs unchanged - only Google's network is faked.

import { AddressComponentLike } from './parse'

interface MockPlace {
  label: string
  components: AddressComponentLike[]
}

const comp = (
  type: string,
  longText: string,
  shortText: string = longText
): AddressComponentLike => ({ types: [type], longText, shortText })

const VIC = comp('administrative_area_level_1', 'Victoria', 'VIC')
const AU = comp('country', 'Australia', 'AU')

const MOCK_PLACES: MockPlace[] = [
  {
    label: '12 Example Street, Fitzroy VIC 3065',
    components: [
      comp('street_number', '12'),
      comp('route', 'Example Street', 'Example St'),
      comp('locality', 'Fitzroy'),
      VIC,
      comp('postal_code', '3065'),
      AU,
    ],
  },
  {
    label: '1 Collins Street, Melbourne VIC 3000',
    components: [
      comp('street_number', '1'),
      comp('route', 'Collins Street', 'Collins St'),
      comp('locality', 'Melbourne'),
      VIC,
      comp('postal_code', '3000'),
      AU,
    ],
  },
  {
    label: '5/34 Chapel Street, Prahran VIC 3181',
    components: [
      comp('subpremise', '5'),
      comp('street_number', '34'),
      comp('route', 'Chapel Street', 'Chapel St'),
      comp('locality', 'Prahran'),
      VIC,
      comp('postal_code', '3181'),
      AU,
    ],
  },
  {
    label: '200 Latrobe Terrace, Geelong West VIC 3218',
    components: [
      comp('street_number', '200'),
      comp('route', 'Latrobe Terrace', 'Latrobe Tce'),
      comp('locality', 'Geelong West'),
      VIC,
      comp('postal_code', '3218'),
      AU,
    ],
  },
  {
    label: '88 George Street, Sydney NSW 2000 (not Victorian)',
    components: [
      comp('street_number', '88'),
      comp('route', 'George Street', 'George St'),
      comp('locality', 'Sydney'),
      comp('administrative_area_level_1', 'New South Wales', 'NSW'),
      comp('postal_code', '2000'),
      AU,
    ],
  },
]

// Shape a mock place like an AutocompleteSuggestion: the prediction's .text
// carries the label, .toPlace() yields the components after fetchFields.
const toSuggestion = (place: MockPlace) => ({
  placePrediction: {
    text: { text: place.label },
    toPlace: () => ({
      fetchFields: () => Promise.resolve(),
      addressComponents: place.components,
    }),
  },
})

export const installMockPlaces = () => {
  const globals = window as unknown as {
    google?: { maps?: { places?: Record<string, unknown> } }
  }
  globals.google = globals.google ?? {}
  globals.google.maps = globals.google.maps ?? {}
  const places = (globals.google.maps.places = globals.google.maps.places ?? {})
  places.AutocompleteSessionToken = class {}
  places.AutocompleteSuggestion = {
    fetchAutocompleteSuggestions: ({ input }: { input: string }) => {
      const query = input.trim().toLowerCase()
      const suggestions = query
        ? MOCK_PLACES.filter((place) =>
            place.label.toLowerCase().includes(query)
          ).map(toSuggestion)
        : []
      return Promise.resolve({ suggestions })
    },
  }
}
