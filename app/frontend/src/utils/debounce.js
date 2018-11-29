/*
Debounces user input. Example usage:

  // Create a function which will debounce every 300ms
  debounce300 = debounce(300)

  // Add a callback
  const alertHello = () => alert('hello')
  alertDebounce = debounce300(alertHello)

  // Call the debouncer. If it is not called again in the next 300ms,
  // then it will call `alertHello`
  alertDebounce()

*/
export default delay => {
  let timer = null
  return callback => {
    return (...args) => {
      clearTimeout(timer)
      timer = setTimeout(() => callback(...args), delay)
    }
  }
}
