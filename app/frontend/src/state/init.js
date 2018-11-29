// Default schema for backend data
const dataDefault = {
  loading: true, // Whether the data is loading from the backend
  lookup: {}, // Lookup table of the data, indexed by 'id'
  list: [], // List of all the data (exactly the same elements as lookup)
}

// Initial Redux state for the app
export default {
  // Data from the backend
  data: {
    script: { ...dataDefault },
    question: { ...dataDefault },
    submission: { ...dataDefault },
  },
  // Selection data - whether elements are open / closed etc.
  selection: {
    question: {
      open: {},
    },
    transition: {
      open: {},
    },
  },
  // Error messages
  error: {
    errors: null,
    visible: false,
  },
}
