import { ElementFactory, QuestionNonValue, Serializer } from 'survey-core'

// The submit page's answer review is our own React panel (see
// comps/AnswerReview) mounted as a SurveyJS question, so it sits inside the
// page - above the Back / Send buttons - rather than below the card. Only the
// model side is registered here, since the form model is built without React
// (the tests do it too); the renderer registers itself against this type in the
// component. A non-value question holds no answer, title or input of its own.
export const REVIEW_QUESTION_TYPE = 'intake-review'

export class QuestionReviewModel extends QuestionNonValue {
  getType(): string {
    return REVIEW_QUESTION_TYPE
  }
}

ElementFactory.Instance.registerElement(
  REVIEW_QUESTION_TYPE,
  (name) => new QuestionReviewModel(name)
)

Serializer.addClass(
  REVIEW_QUESTION_TYPE,
  [],
  () => new QuestionReviewModel(''),
  'nonvalue'
)
