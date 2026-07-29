import { Model } from 'survey-core'

import { buildAnswerSummary } from '../form/review'

interface Props {
  survey: Model
  // Jump back to a section's first page to edit it (see useFormNavigation's
  // editSection).
  onEdit: (sectionIndex: number) => void
}

/**
 * The submit-page answer review: the user's answers grouped by section, each
 * section carrying an Edit link that jumps back to it. Disclosed by the ghost
 * "Review your answers" button in the navigation bar (see nav-items +
 * useFormNavigation); FormPage renders this panel only while that is expanded.
 * The summary is read from survey.data at render time (see form/review), so it
 * always reflects the latest answers.
 */
export const AnswerReview = ({ survey, onEdit }: Props) => {
  const summary = buildAnswerSummary(survey)
  // Nothing answered (shouldn't happen on the submit page) - render nothing.
  if (summary.length === 0) return null
  return (
    <div className="intake-review" role="region" aria-label="Your answers">
      {summary.map((section) => (
        <section key={section.index} className="intake-review__section">
          <div className="intake-review__head">
            <h3 className="intake-review__title">{section.label}</h3>
            <button
              type="button"
              className="intake-review__edit"
              onClick={() => onEdit(section.index)}
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
  )
}
