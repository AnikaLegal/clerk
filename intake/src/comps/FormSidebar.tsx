import { useEffect, useState } from 'react'
import { getTocRootCss } from 'survey-core'
import { List } from 'survey-react-ui'

import { SectionListOptions, useSectionList } from './useSectionList'

export interface FormNavProps extends SectionListOptions {
  // When the answers were last written down, for the save state; null before
  // this visit has saved anything.
  lastSavedAt?: number | null
  // Leaves the form for good: emails the resume link where there is an address
  // to send it to, then shows the way out. Omitted where there is nothing left
  // to come back to.
  onSaveExit?: () => void
}

/**
 * The form's side navigation on wide screens: the section list (see
 * useSectionList) docked as a rail beside the question column, with the
 * progress summary above it and the save state below.
 */
export const FormSidebar = ({
  survey,
  visited,
  onJump,
  sent = false,
  readOnly = false,
  lastSavedAt = null,
  onSaveExit,
}: FormNavProps) => {
  const { list, summary } = useSectionList({
    survey,
    visited,
    onJump,
    sent,
    readOnly,
  })

  return (
    <nav
      className={`intake-sidebar${readOnly ? ' intake-sidebar--readonly' : ''}`}
      aria-label="Form sections"
    >
      {/* The rail is banded like the question column: a head holding the
          progress summary, the section list, and a foot whose hairline
          continues the one above the Back / Continue buttons. */}
      <div className="intake-sidebar__head">
        <span className="intake-sidebar__title">Your progress</span>
        <ProgressMeter percent={summary.percent} />
        <span className="intake-sidebar__subtitle">
          {summary.doneCount} of {summary.sectionCount} done
        </span>
      </div>
      <div className="intake-sidebar__list intake-nav-list">
        <div className={getTocRootCss(survey)}>
          <List model={list} />
        </div>
      </div>
      <div className="intake-sidebar__foot">
        <SaveState lastSavedAt={lastSavedAt} />
        {onSaveExit && <SaveExitButton onClick={onSaveExit} />}
      </div>
    </nav>
  )
}

// One continuous bar filled to the whole form's completion.
export const ProgressMeter = ({ percent }: { percent: number }) => (
  <div
    className="intake-nav__meter"
    role="progressbar"
    aria-label="Form progress"
    aria-valuemin={0}
    aria-valuemax={100}
    aria-valuenow={percent}
  >
    <div className="intake-nav__meter-fill" style={{ width: `${percent}%` }} />
  </div>
)

// The way out of the form, as a text link rather than a button: leaving is not
// an action to press, and the answers are saved either way.
export const SaveExitButton = ({ onClick }: { onClick: () => void }) => (
  <button type="button" className="intake-sidebar__save-exit" onClick={onClick}>
    Save &amp; finish later
  </button>
)

// How long ago the answers were written down, in words. Kept coarse: the point
// is "your work is not going anywhere", not the exact second.
const savedAgo = (lastSavedAt: number): string => {
  const minutes = Math.floor((Date.now() - lastSavedAt) / 60_000)
  if (minutes < 1) return 'Saved just now'
  if (minutes === 1) return 'Saved 1 minute ago'
  if (minutes < 60) return `Saved ${minutes} minutes ago`
  const hours = Math.floor(minutes / 60)
  return hours === 1 ? 'Saved 1 hour ago' : `Saved ${hours} hours ago`
}

// The save state, re-read on a timer so "just now" doesn't sit there for an
// hour while the user thinks about an answer.
export const SaveState = ({ lastSavedAt }: { lastSavedAt: number | null }) => {
  const [, tick] = useState(0)
  useEffect(() => {
    if (lastSavedAt === null) return
    const timer = setInterval(() => tick((n) => n + 1), 30_000)
    return () => clearInterval(timer)
  }, [lastSavedAt])
  return (
    <span className="intake-sidebar__saved">
      {lastSavedAt === null ? 'Saves as you go' : savedAgo(lastSavedAt)}
    </span>
  )
}
