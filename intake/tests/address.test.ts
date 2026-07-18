import { describe, expect, it } from 'vitest'

import {
  AddressComponentLike,
  isVictoria,
  parseAddressComponents,
} from '../src/form/address/parse'

// Build a google.maps-style address_components list from a compact map of
// { type: [longText, shortText] }.
const components = (
  map: Record<string, [string, string]>
): AddressComponentLike[] =>
  Object.entries(map).map(([type, [longText, shortText]]) => ({
    types: [type],
    longText,
    shortText,
  }))

const MELBOURNE = components({
  street_number: ['12', '12'],
  route: ['Example Street', 'Example St'],
  locality: ['Fitzroy', 'Fitzroy'],
  administrative_area_level_1: ['Victoria', 'VIC'],
  postal_code: ['3065', '3065'],
  country: ['Australia', 'AU'],
})

describe('parseAddressComponents', () => {
  it('splits a full Victorian address into the intake fields', () => {
    expect(parseAddressComponents(MELBOURNE)).toEqual({
      address: '12 Example Street',
      suburb: 'Fitzroy',
      postcode: '3065',
      state: 'VIC',
    })
  })

  it('prefixes a unit/subpremise onto the street line', () => {
    const parsed = parseAddressComponents(
      components({
        subpremise: ['5', '5'],
        street_number: ['12', '12'],
        route: ['Example Street', 'Example St'],
        locality: ['Fitzroy', 'Fitzroy'],
        administrative_area_level_1: ['Victoria', 'VIC'],
        postal_code: ['3065', '3065'],
      })
    )
    expect(parsed.address).toBe('5/12 Example Street')
  })

  it('falls back to postal_town when locality is absent', () => {
    const parsed = parseAddressComponents(
      components({
        route: ['Example Street', 'Example St'],
        postal_town: ['Sometown', 'Sometown'],
        administrative_area_level_1: ['Victoria', 'VIC'],
      })
    )
    expect(parsed.suburb).toBe('Sometown')
  })

  it('returns empty strings for missing components', () => {
    const parsed = parseAddressComponents(
      components({ route: ['Example Street', 'Example St'] })
    )
    expect(parsed).toEqual({
      address: 'Example Street',
      suburb: '',
      postcode: '',
      state: '',
    })
  })
})

describe('isVictoria', () => {
  it('accepts a VIC address', () => {
    expect(isVictoria(parseAddressComponents(MELBOURNE))).toBe(true)
  })

  it('rejects a non-VIC address', () => {
    const nsw = components({
      route: ['George Street', 'George St'],
      locality: ['Sydney', 'Sydney'],
      administrative_area_level_1: ['New South Wales', 'NSW'],
      postal_code: ['2000', '2000'],
    })
    expect(isVictoria(parseAddressComponents(nsw))).toBe(false)
  })
})
