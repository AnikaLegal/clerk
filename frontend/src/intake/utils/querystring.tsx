// Read querystring parameters from URL
// Returns an object.
import { entries } from './functional'

export const getQueryParams = () => parseQueryString(window.location.search)

// Reads provided QS params
export const parseQueryString = (qs: string): { [key: string]: string } =>
  (qs.startsWith('?') ? qs.slice(1) : qs)
    .split('&')
    .filter((param) => param)
    .map((paramString) => paramString.split('='))
    .reduce((obj, [k, v]) => ({ ...obj, [k]: v }), {})

// Builds a querystring, including the ?, from obj params.
// Returns a string.
export const buildQueryString = (params: { [key: string]: string }) => {
  const qs = entries(params)
    .map(([k, v]) => [encodeURIComponent(k), encodeURIComponent(v)])
    .map(([k, v]) => `${k}=${v}`)
    .join('&')
  return `?${qs}`
}
