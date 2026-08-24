import { createContext, useContext, useId, useState } from 'react'
import { Model } from 'survey-core'
import { ReactQuestionFactory } from 'survey-react-ui'

import { buildAnswerSummary } from '../form/review'
import { REVIEW_QUESTION_TYPE } from '../form/review-question'

interface ReviewControls {
  survey: Model
  // Jump back to a section's first page to edit it (see useFormNavigation's
  // editSection).
  onEdit: (sectionIndex: number) => void
}

// The review renders inside the survey (see form/review-question), so what it
// needs is handed down the React tree rather than through props: SurveyJS
// creates the element, but it still mounts under FormPage's <Survey>.
export const ReviewContext = createContext<ReviewControls | null>(null)

/**
 * The submit page's answer review: a row that says what the answers are ("Check
 * my answers - 25 answers across 6 sections") with the answers themselves
 * collapsed behind it, so sending stays one button away and nobody has to leave
 * the page to look. Opening it lists the answers grouped by section, each
 * section carrying an Edit link back into it.
 *
 * The summary is read from survey.data at render time (see form/review), so it
 * always reflects the latest answers.
 */
export const AnswerReview = () => {
  const controls = useContext(ReviewContext)
  const [open, setOpen] = useState(false)
  const panelId = useId()
  // Rendered by SurveyJS, so the context can be missing in isolation.
  if (!controls) return null
  const summary = buildAnswerSummary(controls.survey)
  // Nothing answered (shouldn't happen on the submit page) - render nothing.
  if (summary.length === 0) return null
  const answerCount = summary.reduce(
    (total, section) => total + section.rows.length,
    0
  )

  return (
    <div className="intake-review">
      <button
        type="button"
        className="intake-review__toggle"
        aria-expanded={open}
        aria-controls={panelId}
        onClick={() => setOpen((wasOpen) => !wasOpen)}
      >
        <span className="intake-review__toggle-label">Check my answers</span>
        <span className="intake-review__toggle-count">
          {answerCount} answer{answerCount === 1 ? '' : 's'} across{' '}
          {summary.length} section{summary.length === 1 ? '' : 's'}
        </span>
        <span className="intake-review__chevron" aria-hidden="true" />
      </button>
      <div
        id={panelId}
        className="intake-review__panel"
        role="region"
        aria-label="Your answers"
        hidden={!open}
      >
        {summary.map((section) => (
          <section key={section.index} className="intake-review__section">
            <div className="intake-review__head">
              <h3 className="intake-review__title">{section.label}</h3>
              <button
                type="button"
                className="intake-review__edit"
                onClick={() => controls.onEdit(section.index)}
                aria-label={`Edit ${section.label}`}
              >
                Edit
              </button>
            </div>
            <dl className="intake-review__list">
              {section.rows.map((row) => (
                <div key={row.name} className="intake-review__row">
                  <dt className="intake-review__label">{row.label}</dt>
                  <dd className="intake-review__value">{row.value}</dd>
                </div>
              ))}
            </dl>
          </section>
        ))}
      </div>
    </div>
  )
}

ReactQuestionFactory.Instance.registerQuestion(REVIEW_QUESTION_TYPE, () => (
  <AnswerReview />
))
