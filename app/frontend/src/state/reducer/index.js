import generic from './generic'
import error from './error'
import selection from './selection'

// Combine all our reducers into a single reducer lookup table.
const reducer = {
  ...error,
  ...generic,
  ...selection,
}

// The final reducer function, which we pass to Redux.
export default (state, action) => {
  const func = reducer[action.type]
  if (!func) return { ...state }
  return func(state, action)
}
