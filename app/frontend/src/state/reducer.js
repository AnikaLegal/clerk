
const buildNewQuestion = id => ({
  id: id,
  prompt: '',
  type: '',
  options: [],
  follows: [],
  start: false,
})

const question = {
  CREATE_QUESTION: (state, action) => ({
    ...state,
    script: {
      ...state.script,
      [action.id]: buildNewQuestion(action.id)
    },
  }),
  UPDATE_QUESTION: (state, action) => {
    return {
      ...state,
      script: { ...state.script, [action.question.id]: action.question },
    }
  },
  REMOVE_QUESTION: (state, action) => {
    const script = { ...state.script }
    delete script[action.id]
    return {
      ...state,
      script: script,
    }
  },
  ADD_FOLLOWS: (state, action) => {
    const question = state.script[action.id]
    return {
      ...state,
      script: {
        ...state.script,
        [question.id]: {
          ...question,
          follows: [
            ...question.follows,
            {
              id: action.prev,
              when: action.when ? { id: action.when, value: action.value} : null,
            },
          ]
        }
      }
    }
  },
  REMOVE_FOLLOWS: (state, action) => {
    const follows = action.follows
    const question = { ...state.script[action.id] }
    question.follows = question.follows
      .filter(f => {
        // Filter out the follows that we want to remove
        const isMatchPrevId = f.id === follows.id
        const isMatchWhen = (
          (!f.when && !follows.when) ||
          f.when && follows.when &&
          f.when.id === follows.when.id &&
          f.when.value === follows.when.value
        )
        return !(isMatchPrevId && isMatchWhen)
      })

    return {
      ...state,
      script: { ...state.script, [question.id]: question },
    }
  },
}

const script = {
  UPLOAD_SCRIPT: (state, action) => ({
    ...state,
    script: action.script,
  }),
}

const reducers = {
  ...question,
  ...script,
  UPSERT_ITEM: (state, action) => ({
    ...state,
    data: {
      ...state.data,
      [action.key]: {
        ...state.data[action.key],
        loading: action.loading || false,
        lookup: { ...state.data[action.key].lookup, [action.item.id]: action.item },
        list: isItemInList(action.item, state.data[action.key].list) ?
          updateItemInList(action.item, state.data[action.key].list) :
          addItemToList(action.item, state.data[action.key].list),
      },
    },
  }),
  // Mark a set of data items as "loading"
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
        isCached: true,
        loading: false,
        list: action.data,
        lookup: action.data.reduce((obj, el) => { obj[el.id] = el; return obj; }, {}),
      },
    },
  }),
}

export default (state, action) => {
  const func = reducers[action.type]
  if (!func) return { ...state }
  return func(state, action)
}
