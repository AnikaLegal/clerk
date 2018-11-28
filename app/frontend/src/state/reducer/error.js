// Update the state for error data
const error = {
  // Set the errors
  WRITE_ERROR: (state, action) => ({
    ...state,
    error: {
      ...state.error,
      errors: action.errors,
    },
  }),
  // Display the errors
  SHOW_ERROR: state => ({
    ...state,
    error: {
      ...state.error,
      visible: true,
    },
  }),
  // Hii
  CLEAR_ERROR: state => ({
    ...state,
    // Set all data items to 'not loading'
    data: Object.entries(state.data)
      .map(([key, data]) => [key, { ...data, loading: false }])
      .reduce((obj, [key, data]) => {
        obj[key] = data
        return obj
      }, {}),
    error: {
      ...state.error,
      errors: null,
      visible: false,
    },
  }),
}

export default error
