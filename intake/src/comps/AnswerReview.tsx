import { createContext, useContext, useId } from 'react'
import { Model } from 'survey-core'
import { ReactQuestionFactory } from 'survey-react-ui'

import { buildAnswerSummary } from '../form/review'
import { REVIEW_QUESTION_TYPE } from '../form/review-question'

interface ReviewControls {
  survey: Model
  // Go back to the page holding one answer to change it, and return here after
  // (see useFormNavigation's editAnswer).
  onEdit: (questionName: string) => void
  open: boolean
  setOpen: (open: boolean) => void
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
  const panelId = useId()
  // Rendered by SurveyJS, so the context can be missing in isolation.
  if (!controls) return null
  const { open, setOpen } = controls
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
        onClick={() => setOpen(!open)}
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
            <h3 className="intake-review__title">{section.label}</h3>
            <dl className="intake-review__list">
              {section.rows.map((row) => (
                <div key={row.name} className="intake-review__row">
                  <dt className="intake-review__label">{row.label}</dt>
                  <dd className="intake-review__value">{row.value}</dd>
                  <dd className="intake-review__action">
                    <button
                      type="button"
                      className="intake-review__edit"
                      onClick={() => controls.onEdit(row.name)}
                    >
                      Change
                      {/* Every row's link reads "Change", so name what it
                          changes for anyone listening rather than looking. */}
                      <span className="intake-visually-hidden">
                        {' '}
                        {row.label}
                      </span>
                    </button>
                  </dd>
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
