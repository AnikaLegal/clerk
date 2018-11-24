const question = {
  CREATE_QUESTION: (state, action) => ({
    ...state,
    script: {
      ...state.script,
      [action.id]: {
        id: action.id,
      },
    },
  }),
  UPDATE_QUESTION: (state, action) => {
    const script = { ...state.script }
    script[action.question.id] = action.question
    return {
      ...state,
      script: script,
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
}

export default (state, action) => {
  const func = reducers[action.type]
  if (!func) return { ...state }
  return func(state, action)
}
