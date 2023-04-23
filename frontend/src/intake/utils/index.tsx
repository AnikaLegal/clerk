export * from './querystring'
export * from './debounce'
export * from './functional'
export * from './format'
export * from './storage'

export const timeout = (ms: number) =>
  new Promise<void>((r) => setTimeout(r, ms))
