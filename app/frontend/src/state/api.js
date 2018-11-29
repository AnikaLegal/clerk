import urls from 'urls'
import http from 'utils/http'

// All HTTP API calls made by the frontend
export default {
  script: {
    // List all scripts
    list: () => http.get(urls.api.script.list()),
    // Create a new script
    create: ({ name }) =>
      http.post(urls.api.script.list(), {
        name: name,
        first_question: null,
      }),
    // Set a 'first question' on a script
    setFirstQuestion: ({ scriptId, firstQuestionId }) =>
      http.patch(urls.api.script.details(scriptId), {
        first_question: firstQuestionId,
      }),
  },
  question: {
    // List all questions
    list: () => http.get(urls.api.question.list()),
    // Create a new question
    create: ({ scriptId, name, prompt, fieldType }) =>
      http.post(urls.api.question.list(), {
        name: name,
        prompt: prompt,
        field_type: fieldType,
        script: scriptId,
      }),
    // Update an existing question
    update: ({ questionId, name, prompt, fieldType }) =>
      http.patch(urls.api.question.details(questionId), {
        name: name,
        prompt: prompt,
        field_type: fieldType,
      }),
    // Delete an existing question
    delete: ({ questionId }) =>
      http.delete(urls.api.question.details(questionId)),
  },
  transition: {
    // Create a new transition (returns a question object)
    create: ({ questionId, previous, condition, variable, value }) =>
      http.post(urls.api.transition.list(), {
        next: questionId,
        previous: previous,
        condition: condition,
        variable: variable,
        value: value,
      }),
    // Delete an existing transition (returns a question object)
    delete: ({ transitionId }) =>
      http.delete(urls.api.transition.details(transitionId)),
    // Update an existing transition (returns a question object)
    update: ({
      transitionId,
      questionId,
      previous,
      condition,
      variable,
      value,
    }) =>
      http.put(urls.api.transition.details(transitionId), {
        next: questionId,
        previous: previous,
        condition: condition,
        variable: variable,
        value: value,
      }),
  },
}
