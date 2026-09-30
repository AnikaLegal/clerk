import { useCallback, useEffect, useId, useRef, useState } from 'react'
import { getTocRootCss } from 'survey-core'
import { List } from 'survey-react-ui'

import { FormNavProps } from './FormSidebar'
import { ProgressMeter, SaveExitButton, SaveState } from './FormSidebar'
import { useSectionList } from './useSectionList'

/**
 * The form's navigation on narrow screens, where the rail has no room: one
 * bar pinned above the questions saying where the user is and how far along,
 * which opens the full section list as a sheet from the bottom of the screen.
 * The sheet is a native modal dialog, which gives the focus trap, Escape and
 * the return of focus to the bar on close.
 */
export const MobileNav = ({
  survey,
  visited,
  onJump,
  sent = false,
  readOnly = false,
  lastSavedAt = null,
  onSaveExit,
}: FormNavProps) => {
  const dialogRef = useRef<HTMLDialogElement>(null)
  const [open, setOpen] = useState(false)
  const titleId = useId()

  const close = useCallback(() => dialogRef.current?.close(), [])

  // Picking a section is also what closes the sheet: the user is on their way.
  const jumpAndClose = useCallback(
    (sectionIndex: number) => {
      onJump(sectionIndex)
      close()
    },
    [onJump, close]
  )

  const { list, summary } = useSectionList({
    survey,
    visited,
    onJump: jumpAndClose,
    sent,
    readOnly,
  })

  // The page behind the sheet must not scroll under it while it is open.
  useEffect(() => {
    if (!open) return
    const previous = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    return () => {
      document.body.style.overflow = previous
    }
  }, [open])

  // Save & finish later leaves the form, so the sheet goes first.
  const saveExit = onSaveExit
    ? () => {
        close()
        onSaveExit()
      }
    : undefined

  return (
    <div className="intake-mobile-nav">
      <div className="intake-mobile-nav__row">
        <span className="intake-mobile-nav__title">{summary.title}</span>
        <button
          type="button"
          className="intake-mobile-nav__open"
          aria-haspopup="dialog"
          aria-expanded={open}
          onClick={() => {
            dialogRef.current?.showModal()
            setOpen(true)
          }}
        >
          {/* The focus ring goes on the label: the button's 44px target
              reaches past the row's one line of text, over the meter. */}
          <span className="intake-mobile-nav__open-label">
            All steps
            <span className="intake-mobile-nav__chevron" aria-hidden="true" />
          </span>
        </button>
      </div>
      <ProgressMeter percent={summary.percent} />
      <span className="intake-mobile-nav__subtitle">{summary.subtitle}</span>

      {/* A click on the dialog itself, outside the sheet's panel, is a tap on
          the scrim. */}
      <dialog
        ref={dialogRef}
        className={`intake-sheet${readOnly ? ' intake-sheet--readonly' : ''}`}
        aria-labelledby={titleId}
        onClose={() => setOpen(false)}
        onClick={(event) => {
          if (event.target === event.currentTarget) close()
        }}
      >
        <div className="intake-sheet__panel">
          <div className="intake-sheet__head">
            <div className="intake-sheet__summary">
              <span id={titleId} className="intake-sidebar__title">
                Your progress
              </span>
              <span className="intake-sidebar__subtitle">
                {summary.doneCount} of {summary.sectionCount} done
              </span>
            </div>
            <button
              type="button"
              className="intake-sheet__close"
              aria-label="Close"
              onClick={close}
            />
          </div>
          <nav
            className="intake-sheet__list intake-nav-list"
            aria-label="Form sections"
          >
            <div className={getTocRootCss(survey)}>
              <List model={list} />
            </div>
          </nav>
          <div className="intake-sheet__foot">
            <SaveState lastSavedAt={lastSavedAt} />
            {saveExit && <SaveExitButton onClick={saveExit} />}
          </div>
        </div>
      </dialog>
    </div>
  )
}
