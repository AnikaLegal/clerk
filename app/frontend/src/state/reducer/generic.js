// Generic operations on backend API data
const generic = {
  // Update or insert a single data item, based on id
  UPSERT_ITEM: (state, action) => ({
    ...state,
    data: {
      ...state.data,
      [action.key]: {
        ...state.data[action.key],
        loading: action.loading || false,
        lookup: {
          ...state.data[action.key].lookup,
          [action.item.id]: action.item,
        },
        list: isItemInList(action.item, state.data[action.key].list)
          ? updateItemInList(action.item, state.data[action.key].list)
          : addItemToList(action.item, state.data[action.key].list),
      },
    },
  }),
  // Remove a single data item, based on id
  REMOVE_ITEM: (state, action) => ({
    ...state,
    data: {
      ...state.data,
      [action.key]: {
        ...state.data[action.key],
        loading: false,
        lookup: removeItemFromLookup(
          action.item,
          state.data[action.key].lookup
        ),
        list: removeItemFromList(action.item, state.data[action.key].list),
      },
    },
  }), // Mark a set of data items as "loading"
  SET_LOADING: (state, action) => ({
    ...state,
    data: {
      ...state.data,
      [action.key]: {
        ...state.data[action.key],
        loading: true,
      },
    },
  }),
  // Mark a set of data items as not "loading"
  UNSET_LOADING: (state, action) => ({
    ...state,
    data: {
      ...state.data,
      [action.key]: {
        ...state.data[action.key],
        loading: false,
      },
    },
  }),
  // Received a set of data items from the backend
  RECEIVE_LIST: (state, action) => ({
    ...state,
    data: {
      ...state.data,
      [action.key]: {
        loading: false,
        list: action.data,
        lookup: action.data.reduce((obj, el) => {
          obj[el.id] = el
          return obj
        }, {}),
      },
    },
  }),
}

// Helper functions
const isItemInList = (item, list) => list.map(el => el.id).includes(item.id)
const addItemToList = (item, list) => [...list, item]
const updateItemInList = (item, list) =>
  list.map(el => (el.id === item.id ? item : el))
const removeItemFromList = (item, list) => list.filter(el => el.id !== item.id)
const removeItemFromLookup = (item, lookup) => {
  const newLookup = { ...lookup }
  delete newLookup[item.id]
  return newLookup
}

export default generic
