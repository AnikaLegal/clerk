// initial state for the app
const dataDefault = { loading: true, lookup: {}, list: [] };

export default {
  script: {},
  data: {
  	// Data from the backend
  	script: { ...dataDefault },
  	answer: { ...dataDefault },
  }
}
