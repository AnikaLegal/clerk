import { Fragment } from 'react'

import { SECTIONS } from '../questions'

interface Props {
  // Index of the current section in SECTIONS (drives the visual dots).
  current: number
  // Current page number and total, used for the progressbar's value. The
  // visual is section-based, but the finer page count gives assistive tech
  // more useful progress than the six sections - and carries the "Page x of y"
  // that the visual nav-bar count is hidden from AT (see useFormNavigation).
  page: number
  pageCount: number
}

/**
 * A section-based progress stepper (Getting started / About you / ...), shown
 * above the survey in place of the built-in per-page progress bar. Mirrors the
 * previous intake form: a row of connected dots with the current section's
 * label beneath it, earlier sections marked done. The visible "Page x of y"
 * count sits in the survey's navigation bar (see FormPage), not here.
 */
export const SectionProgress = ({ current, page, pageCount }: Props) => (
  <div
    className="intake-progress"
    role="progressbar"
    aria-label="Form progress"
    aria-valuemin={1}
    aria-valuemax={pageCount}
    aria-valuenow={page}
    aria-valuetext={`Page ${page} of ${pageCount}, ${SECTIONS[current]?.label}`}
  >
    <div className="intake-progress__steps">
      {SECTIONS.map((section, idx) => {
        const state =
          idx < current ? 'is-done' : idx === current ? 'is-current' : ''
        return (
          <Fragment key={section.label}>
            <div className={`intake-progress__step ${state}`}>
              <span className="intake-progress__dot" />
              {idx === current && (
                <span className="intake-progress__label">{section.label}</span>
              )}
            </div>
            {idx < SECTIONS.length - 1 && (
              <span
                className={`intake-progress__bar ${idx < current ? 'is-done' : ''}`}
              />
            )}
          </Fragment>
        )
      })}
    </div>
  </div>
)
