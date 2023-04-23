// Debounce user input
export const debounce = (delay: number) => {
  let timer = null
  return (func: Function) => {
    return (...args: Array<any>) => {
      clearTimeout(timer)
      timer = setTimeout(() => func(...args), delay)
    }
  }
}

// Debounce user input, returns a promise
export const debouncePromise = (delay: number) => {
  let timer = null
  return (func: Function) => {
    return (...args: Array<any>): Promise<any> =>
      new Promise((resolve) => {
        clearTimeout(timer)
        timer = setTimeout(() => func(...args).then(resolve), delay)
      })
  }
}

// Wait n seconds
export const waitSeconds = (delay: number): Promise<void> =>
  new Promise((resolve) => setTimeout(() => resolve(), delay * 1000))
