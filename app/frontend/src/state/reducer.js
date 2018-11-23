const question = {
  CREATE_QUESTION: (state, action) => ({
    ...state,
    script: {
      ...state.script,
      [action.name]: {
        name: action.name,
      },
    }
  }),
  UPDATE_QUESTION: (state, action) => {
    const script = {...state.script}
    delete script[action.prevName]
    script[action.question.name] = action.question
    return {
      ...state,
      script: script
    }
  },
  REMOVE_QUESTION: (state, action) => {
    const script = {...state.script}
    delete script[action.name]
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
  })
}

const reducers = {
  ...question,
  ...script,
}


export default (state, action) => {
  const func = reducers[action.type]
  if (!func) return {...state}
  return func(state, action)
}
