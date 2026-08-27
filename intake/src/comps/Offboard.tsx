import { ReactNode } from 'react'
import { useNavigate } from 'react-router-dom'

import { LINKS, ROUTES } from '../consts'
import { useAnnouncePage } from '../views/announce'

// At most one primary action - a route/outbound link or a button. Outbound
// links are visually marked as leaving (trailing arrow + new tab).
export interface OffboardPrimary {
  label: string
  href?: string
  onClick?: () => void
  external?: boolean
}

export interface OffboardProps {
  // The outcome itself, in plain words - not "Sorry" or "Oops".
  headline: string
  // Max two sentences - why, and what it means for them.
  explanation: ReactNode
  // Optional body slot: the only part that changes shape between pages -
  // referral cards, a next-steps list, or a form.
  children?: ReactNode
  // Optional primary action: omitted only when no onward action exists.
  primary?: OffboardPrimary
  // Optional: what happens to the answers they already gave - saved,
  // deleted, or sent. One line.
  dataNote?: ReactNode
}

// A referral card for the body slot: an outbound link presented as a card
// carrying the organisation's name and what they offer. The optional tag is
// a short lookup key rendered in its own left section (e.g. the state
// acronym on the outside-Victoria page) so users can scan for the card that
// applies to them.
export const OffboardReferral = ({
  name,
  description,
  href,
  tag,
}: {
  name: string
  description: string
  href: string
  tag?: string
}) => (
  <a
    className="intake-offboard__referral"
    href={href}
    target="_blank"
    rel="noreferrer"
  >
    {tag && <span className="intake-offboard__referral-tag">{tag}</span>}
    <span className="intake-offboard__referral-body">
      <span className="intake-offboard__referral-name">
        {name} <span aria-hidden="true">{'↗'}</span>
      </span>
      <span className="intake-offboard__referral-desc">{description}</span>
    </span>
  </a>
)

/**
 * The offboarding template: every page that takes someone out of the form -
 * ineligible, out of area, we can't help, no email - is this same skeleton
 * with slots switched on or off. The escape-links slot is fixed: always
 * "Go back" first, then the home page, as text links. Never styled as an
 * error - the person did nothing wrong.
 */
export const Offboard = ({
  headline,
  explanation,
  children,
  primary,
  dataNote,
}: OffboardProps) => {
  const navigate = useNavigate()
  const headingRef = useAnnouncePage(headline)
  // Exit URLs are shareable, so a user can arrive with no in-app history (a
  // link from a caseworker, a new tab from browser history). navigate(-1)
  // would then do nothing or leave the site, so at the history floor go to
  // the form instead - it resumes from localStorage, landing them back where
  // they were.
  const goBack = () => {
    const idx = (window.history.state as { idx?: number } | null)?.idx ?? 0
    if (idx === 0) {
      navigate(ROUTES.LANDING)
    } else {
      navigate(-1)
    }
  }
  return (
    <div className="intake-form intake-offboard-page">
      <div className="intake-offboard">
        <h1
          className="intake-offboard__headline"
          tabIndex={-1}
          ref={headingRef}
        >
          {headline}
        </h1>
        <p className="intake-offboard__explanation">{explanation}</p>
        {children}
        {primary &&
          (primary.href ? (
            <a
              className="intake-offboard__primary"
              href={primary.href}
              {...(primary.external
                ? { target: '_blank', rel: 'noreferrer' }
                : {})}
            >
              {primary.label}
              {primary.external && <span aria-hidden="true"> {'↗'}</span>}
            </a>
          ) : (
            <button
              type="button"
              className="intake-offboard__primary"
              onClick={primary.onClick}
            >
              {primary.label}
            </button>
          ))}
        <div className="intake-offboard__links">
          <button
            type="button"
            className="intake-offboard__back"
            onClick={goBack}
          >
            <span aria-hidden="true">{'←'}</span> Go back
          </button>
          <a className="intake-offboard__home" href={LINKS.HOME}>
            Go to the Anika Legal home page
          </a>
        </div>
        {dataNote && <div className="intake-offboard__note">{dataNote}</div>}
      </div>
    </div>
  )
}
