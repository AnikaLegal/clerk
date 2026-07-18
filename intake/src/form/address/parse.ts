// Pure helpers that turn a Google Places address into the intake form's
// structured fields. Kept free of any DOM / google.maps dependency so they are
// straightforward to unit test (see tests/address.test.ts).

// The subset of a google.maps.places.AddressComponent we rely on. Declared
// locally so the parser doesn't depend on the ambient google types (which only
// exist at build time via @types/google.maps).
export interface AddressComponentLike {
  types: string[]
  longText: string | null
  shortText: string | null
}

export interface ParsedAddress {
  // Street line, e.g. "12 Example Street" or "5/12 Example Street".
  address: string
  // Suburb / locality.
  suburb: string
  // Postcode, as a string of digits (may be empty for some rural addresses).
  postcode: string
  // State short code, e.g. "VIC".
  state: string
}

const find = (
  components: AddressComponentLike[],
  type: string
): AddressComponentLike | undefined =>
  components.find((component) => component.types.includes(type))

const longText = (components: AddressComponentLike[], type: string): string =>
  find(components, type)?.longText ?? ''

const shortText = (components: AddressComponentLike[], type: string): string =>
  find(components, type)?.shortText ?? ''

/**
 * Map Google Places address components to the intake ADDRESS / SUBURB /
 * POSTCODE fields. The street line joins the street number and route, prefixed
 * with any unit/subpremise (e.g. "5/12 Example Street"); the suburb falls back
 * to postal_town when locality is absent; the state is the short code (VIC).
 */
export const parseAddressComponents = (
  components: AddressComponentLike[]
): ParsedAddress => {
  const streetNumber = longText(components, 'street_number')
  const route = longText(components, 'route')
  const subpremise = longText(components, 'subpremise')
  const streetLine = [streetNumber, route].filter(Boolean).join(' ')
  const address =
    subpremise && streetLine ? `${subpremise}/${streetLine}` : streetLine
  const suburb =
    longText(components, 'locality') || longText(components, 'postal_town')
  const postcode = longText(components, 'postal_code')
  const state = shortText(components, 'administrative_area_level_1')
  return { address, suburb, postcode, state }
}

// Anika only serves renters in Victoria. Suggestions are already biased to VIC,
// but a bordering address can slip through, so selections are validated too.
export const isVictoria = (parsed: ParsedAddress): boolean =>
  parsed.state.toUpperCase() === 'VIC'
