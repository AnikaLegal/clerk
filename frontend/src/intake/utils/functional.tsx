// Helper functions for map and reduce operations

// Flatten an array
export const flattenArray = (arr: Array<any>, sub: Array<any>): Array<any> => [
  ...arr,
  ...sub,
]

// Sort array in descending order
export const sortDesc = (a: any, b: any): number => (a > b ? -1 : 1)

// Sort array in ascending order
export const sortAsc = (a: any, b: any): number => (a > b ? 1 : -1)

// Ensure primitive item in array is unique
export const unique = (val: any, idx: number, self: Array<any>) =>
  self.indexOf(val) === idx

// All hail our brave new type system - Object.entries doesn't play nice with Flow
// https://github.com/facebook/flow/issues/2174
export const entries = <T,>(obj: { [key: string]: T }): Array<[string, T]> => {
  const keys: string[] = Object.keys(obj)
  return keys.map((key) => [key, obj[key]])
}

export const values = <T,>(obj: { [key: string]: T }): Array<T> => {
  const keys: string[] = Object.keys(obj)
  return keys.map((key) => obj[key])
}
