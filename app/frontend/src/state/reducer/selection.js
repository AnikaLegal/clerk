// Update selection data - whether elements are open / closed etc.
const selection = {
  // Open / close a question form
  TOGGLE_QUESTION_OPEN: (state, action) => {
    const nextState = { ...state }
    const question = nextState.selection.question
    question.open = {
      ...question.open,
      [action.id]: !question.open[action.id],
    }
    return nextState
  },
  // Open / close a transition form
  TOGGLE_TRANSITION_OPEN: (state, action) => {
    const nextState = { ...state }
    const transition = nextState.selection.transition
    transition.open = {
      ...transition.open,
      [action.id]: !transition.open[action.id],
    }
    return nextState
  },
}

export default selection
