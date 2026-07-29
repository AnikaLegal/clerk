import { Fragment } from 'react'

import { SECTIONS } from '../questions'

interface Props {
  // Index of the current section in SECTIONS (drives the visual dots).
  current: number
  // Current page number and total, surfaced to assistive tech in the nav label
  // (the visible "Page x of y" lives in the survey footer).
  page: number
  pageCount: number
  // Sections the user can jump to right now (index -> first visible page),
  // rendered as buttons. See form/section-nav.ts.
  navigable: Map<number, string>
  onJump: (sectionIndex: number) => void
}

/**
 * A section-based progress stepper (Getting started / About you / ...), shown
 * above the survey. A row of connected dots with the current section's label
 * beneath it, earlier sections marked done. Completed / already-answered
 * sections are buttons the user can click to jump straight to that section's
 * first page (backward, or forward when the pages in between are all answered);
 * see form/section-nav.ts for what counts as navigable. It is a navigation
 * landmark rather than a progressbar now that the steps are interactive - an
 * interactive control inside a progressbar would not be exposed to assistive
 * tech.
 */
export const SectionProgress = ({
  current,
  page,
  pageCount,
  navigable,
  onJump,
}: Props) => (
  <nav
    className="intake-progress"
    aria-label={`Form progress, page ${page} of ${pageCount}`}
  >
    <div className="intake-progress__steps">
      {SECTIONS.map((section, idx) => {
        const state =
          idx < current ? 'is-done' : idx === current ? 'is-current' : ''
        const inner = (
          <>
            <span className="intake-progress__dot" />
            {idx === current && (
              <span className="intake-progress__label">{section.label}</span>
            )}
          </>
        )
        return (
          <Fragment key={section.label}>
            {navigable.has(idx) ? (
              <button
                type="button"
                className={`intake-progress__step intake-progress__step--jump ${state}`}
                onClick={() => onJump(idx)}
                title={section.label}
                aria-label={`Go to ${section.label}`}
              >
                {inner}
              </button>
            ) : (
              <span
                className={`intake-progress__step ${state}`}
                aria-current={idx === current ? 'step' : undefined}
              >
                {inner}
              </span>
            )}
            {idx < SECTIONS.length - 1 && (
              <span
                className={`intake-progress__bar ${idx < current ? 'is-done' : ''}`}
                aria-hidden="true"
              />
            )}
          </Fragment>
        )
      })}
    </div>
  </nav>
)
