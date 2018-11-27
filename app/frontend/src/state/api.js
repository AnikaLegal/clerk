import urls from 'urls'
import http from 'utils/http'

// All HTTP API calls made by the frontend
export default {
  script: {
    // List all scripts
    list: () => http.get(urls.api.script.list()),
    // Create a new script
    create: name =>
      http.post(urls.api.script.list(), {
        name: name,
        first_question: null,
      }),
    setFirstQuestion: (scriptId, firstQuestionId) =>
      http.patch(urls.api.script.details(scriptId), {
        first_question: firstQuestionId,
      }),
  },
  question: {
    // List all questions
    list: () => http.get(urls.api.question.list()),
    // Create a new question
    create: (scriptId, name, prompt, fieldType) =>
      http.post(urls.api.question.list(), {
        name: name,
        prompt: prompt,
        field_type: fieldType,
        script: scriptId,
      }),
  },
}
