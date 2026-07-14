import { Fragment } from 'react'

import { SECTIONS } from '../questions'

interface Props {
  // Index of the current section in SECTIONS.
  current: number
}

/**
 * A section-based progress stepper (Getting started / About you / ...), shown
 * above the survey in place of the built-in per-page progress bar. Mirrors the
 * previous intake form: a row of connected dots with the current section's
 * label beneath it, earlier sections marked done. The "Page x of y" count sits
 * in the survey's navigation bar (see FormPage), not here.
 */
export const SectionProgress = ({ current }: Props) => (
  <div
    className="intake-progress"
    role="progressbar"
    aria-valuemin={1}
    aria-valuemax={SECTIONS.length}
    aria-valuenow={current + 1}
    aria-valuetext={SECTIONS[current]?.label}
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
