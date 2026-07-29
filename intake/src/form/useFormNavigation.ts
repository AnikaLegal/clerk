import { useCallback, useEffect, useRef, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { Model } from 'survey-core'

import { events } from '../analytics'
import { ROUTES } from '../consts'
import { logException } from '../utils'
import { markFormBegun, markStepReported } from './funnel'
import { WELCOME_PAGE } from './model'
import { addNavItems } from './nav-items'
import { applyPageAdvance } from './page-advance'
import { Direction, readProgress } from './progress'
import { firstVisiblePageOfSection, navigableSections } from './section-nav'
import { SubmissionSaver } from './save'
import { serializeAnswers } from './serialize'
import { persistState } from './setup'
import {
  BONDS_MOVE_OUT_PAGE,
  EMAIL_PAGE,
  SECTIONS,
  sectionIndexForPage,
  SUBMIT_PAGE,
} from '../questions'

interface FormNavigation {
  survey: Model
  saver: SubmissionSaver
  visited: Set<string>
  session: string
  // Runs the final submit + post-submit splash (see FormPage); fired on the
  // survey's completion.
  attemptSubmit: () => void
}

// Wires the survey's page-change lifecycle to browser history, per-page funnel
// analytics, eligibility exits, skip defaults, local persistence and the
// custom navigation-bar items, and returns the progress-indicator state. Kept
// out of FormPage so the component is just the model, submit state and render.
export const useFormNavigation = ({
  survey,
  saver,
  visited,
  session,
  attemptSubmit,
}: FormNavigation) => {
  const navigate = useNavigate()
  const location = useLocation()
  const [progress, setProgress] = useState(() => ({
    ...readProgress(survey),
    direction: 'forward' as Direction,
  }))
  // Sections the user can jump to right now (index -> that section's first
  // visible page), recomputed on every page and answer change. Drives the
  // clickable stepper. See section-nav.ts for the reachability rules.
  const [navigable, setNavigable] = useState<Map<number, string>>(new Map())
  // Whether the submit-page answer-review panel is expanded. Toggled by the
  // ghost nav-bar button (see addNavItems), read by FormPage to render the
  // panel, and reset to false whenever the user leaves the submit page.
  const [reviewOpen, setReviewOpen] = useState(false)
  // The review toggle nav item, held so the reviewOpen effect can keep its
  // label and aria-expanded in step with the panel state.
  const reviewToggle = useRef<ReturnType<Model['addNavigationItem']> | null>(
    null
  )
  // Mirrors reviewOpen for the nav-DOM observer, which runs outside React and
  // needs the current value without re-subscribing.
  const reviewOpenRef = useRef(false)

  // Browser history <-> survey page sync, so the browser Back / Forward buttons
  // move between the survey's pages instead of leaving the form. Each page gets
  // its own history entry carrying its name in location.state. lastPage tracks
  // the page recorded at the top of the stack; suppressPush marks a survey page
  // change that is itself mirroring a Back / Forward, so it isn't re-recorded.
  const lastPage = useRef<string | null>(null)
  const suppressPush = useRef(false)
  // Marks a browser-Forward move being replayed through survey.nextPage() so
  // the full forward pipeline (validation, skip defaults, exits, side effects)
  // runs, but the resulting page change is not re-recorded in the history.
  const forwardReconcile = useRef(false)
  // Set when onPageChanging ejects to an exit page, so the reconcile effect
  // knows the blocked Forward move already navigated away and must not try to
  // step the history back in line.
  const exitFired = useRef(false)
  // Direction of the page change in progress, captured in onCurrentPageChanging
  // (which carries it) and read in onCurrentPageChanged (which does not), so a
  // backward move via the survey's Previous button steps back through history
  // rather than pushing a duplicate entry.
  const goingForward = useRef(true)
  // react-router's index of the history entry the form opened on. A backward
  // survey move (Previous) only steps back through browser history when a prior
  // form entry exists above this floor; at the floor - e.g. a resumed session
  // whose earlier pages were never in this browser's history - it replaces the
  // current entry instead, so Previous stays in the form rather than exiting.
  const startIdx = useRef<number | null>(null)
  // Each page's browser-history entry index, recorded as the user moves, so a
  // backward section jump can rewind straight to that entry (keeping the
  // history order consistent with the form) rather than pushing a new one.
  const pageEntryIdx = useRef<Record<string, number>>({})

  const recordPage = useCallback(
    (name: string | null | undefined) => {
      if (!name || lastPage.current === name) return
      // The first real page replaces the initial entry in place (so Back from
      // it leaves the form); later pages push a new entry to move forward over.
      navigate(ROUTES.LANDING, {
        state: { page: name, session },
        replace: lastPage.current === null,
      })
      lastPage.current = name
    },
    [navigate, session]
  )

  // Move the survey to a reachable page by name, keeping browser history in
  // step. Forward moves re-walk Next page by page so the forward pipeline (skip
  // defaults, side effects and - crucially - eligibility exits) runs for each
  // page in between; a changed answer that now disqualifies still ejects rather
  // than being skipped, and reachability guarantees every step passes so it
  // won't stall. Backward moves rewind history to the target page's existing
  // entry so the entry order stays consistent with the form. Runs inside the
  // click handler, so React batches the per-step history updates into one.
  const jumpToPage = useCallback(
    (targetPage: string) => {
      const target = survey.getPageByName(targetPage)
      if (!target || !target.isVisible) return
      const pages = survey.visiblePages
      const currentIndex = pages.indexOf(survey.currentPage)
      const targetIndex = pages.indexOf(target)
      if (currentIndex < 0 || targetIndex < 0 || targetIndex === currentIndex) {
        return
      }

      if (targetIndex > currentIndex) {
        let guard = 0
        while (survey.currentPage !== target && guard < pages.length) {
          const before = survey.currentPage
          exitFired.current = false
          survey.nextPage()
          if (exitFired.current || survey.currentPage === before) return
          guard++
        }
        return
      }

      // Backward: rewind to the target page's existing entry when it is known;
      // a resumed session that never visited the page in this browser falls
      // back to moving the survey directly and replacing the current entry.
      const entryIdx = pageEntryIdx.current[targetPage]
      const currentEntryIdx = (window.history.state as { idx?: number } | null)
        ?.idx
      if (
        entryIdx != null &&
        currentEntryIdx != null &&
        entryIdx < currentEntryIdx
      ) {
        navigate(entryIdx - currentEntryIdx)
        return
      }
      suppressPush.current = true
      lastPage.current = targetPage
      survey.currentPage = target
      suppressPush.current = false
      navigate(ROUTES.LANDING, {
        state: { page: targetPage, session },
        replace: true,
      })
    },
    [survey, navigate, session]
  )

  // Jump to a section's first page from a click on the stepper. Recomputed
  // fresh so a stale render can't offer a page that is no longer reachable.
  const jumpToSection = useCallback(
    (sectionIndex: number) => {
      const targetPage = navigableSections(survey, visited).get(sectionIndex)
      if (targetPage) jumpToPage(targetPage)
    },
    [survey, visited, jumpToPage]
  )

  // Edit a section from the submit-page answer review: jump to its first
  // visible page. Unlike jumpToSection this ignores the "navigable" gate, so
  // the section the submit page sits in (its own, never offered as a forward
  // jump) can still be edited; from the submit page every section is behind the
  // user, so jumpToPage always makes a backward move.
  const editSection = useCallback(
    (sectionIndex: number) => {
      const targetPage = firstVisiblePageOfSection(survey, sectionIndex)
      if (targetPage) jumpToPage(targetPage)
    },
    [survey, jumpToPage]
  )

  // Mirror a browser Back / Forward (location change) onto the survey: move it
  // to the page named in the history entry we landed on.
  useEffect(() => {
    const entry = location.state as { page?: string; session?: string } | null
    const target = entry?.page
    // Ignore entries stamped by an earlier form session (e.g. Back after a
    // submit cleared the state and remounted with a fresh session): honouring
    // them would jump the new empty survey to a mid-form page.
    if (entry?.session !== session) return
    // lastPage null means the initial entry has not been stamped yet (see the
    // mount effect below); ignore any page named in a leftover history entry
    // until then, so the survey opens where setUpForm placed it, not a stale
    // page.
    if (!target || lastPage.current === null || lastPage.current === target)
      return
    if (survey.currentPage?.name === target) {
      lastPage.current = target
      return
    }
    const page = survey.getPageByName(target)
    if (!page || !page.isVisible) {
      // The entry names a page that is no longer visible - the user went back
      // and changed a branching answer that hid it. The browser has already
      // advanced to this entry, so returning here would leave history pointing
      // at an unreachable page (the move looks eaten, and a second Forward then
      // jumps two entries). Realign: replace this entry with the survey's
      // actual page so Back / Forward stay in step with the survey.
      lastPage.current = survey.currentPage?.name ?? null
      navigate(ROUTES.LANDING, {
        state: { page: survey.currentPage?.name, session },
        replace: true,
      })
      return
    }
    const pages = survey.visiblePages
    const delta = pages.indexOf(page) - pages.indexOf(survey.currentPage)
    if (delta <= 0) {
      // Backward: mirror the history move directly - going back to an earlier
      // page is always allowed.
      suppressPush.current = true
      lastPage.current = target
      survey.currentPage = page
      return
    }
    if (delta > 1) {
      // A multi-entry Forward jump (e.g. via the Forward button's long-press
      // menu): unwind one entry at a time; each step lands back in this effect
      // until the move is a single step that the gate below can vet.
      navigate(-1)
      return
    }
    // Single-step Forward: replay it through the survey's own forward pipeline
    // (validation, skip defaults, eligibility exits, side effects) rather than
    // teleporting past it - otherwise going back, changing an answer to a
    // disqualifying one and pressing Forward would walk straight past the exit.
    forwardReconcile.current = true
    exitFired.current = false
    survey.nextPage()
    forwardReconcile.current = false
    if (survey.currentPage?.name !== target && !exitFired.current) {
      // Validation blocked the advance (errors are now showing): step the
      // history back in line with the survey. The reconcile fires again for
      // that entry and finds the survey already there.
      lastPage.current = survey.currentPage?.name ?? null
      navigate(-1)
    }
  }, [location, survey, navigate, session])

  // Stamp the initial history entry for the page the survey opens on (WELCOME
  // for a fresh visitor, or the restored page when resuming). Runs once on
  // mount - recordPage / survey are stable for the component's life.
  useEffect(() => {
    const state = window.history.state as { idx?: number } | null
    startIdx.current = state?.idx ?? 0
    recordPage(survey.currentPage?.name)
  }, [recordPage, survey])

  // Remember the browser-history index of whatever page each entry holds, so a
  // backward section jump can rewind straight to it.
  useEffect(() => {
    const name = (location.state as { page?: string } | null)?.page
    const idx = (window.history.state as { idx?: number } | null)?.idx
    if (name && idx != null) pageEntryIdx.current[name] = idx
  }, [location])

  useEffect(() => {
    const { noEmailItem, notMovingOutItem, pageCountItem, reviewToggleItem } =
      addNavItems(survey, navigate)
    // Toggle the review panel from the ghost nav-bar button; the reviewOpen
    // effect below keeps the button's label and aria-expanded in sync.
    reviewToggle.current = reviewToggleItem
    reviewToggleItem.action = () => setReviewOpen((wasOpen) => !wasOpen)
    // Keep the per-page UI in sync with the current page: the no-email button's
    // visibility, the WELCOME page's "Let's get started" button label, the page
    // count, and the progress stepper's active section.
    const syncPage = () => {
      const p = readProgress(survey)
      const onWelcome = survey.currentPage?.name === WELCOME_PAGE
      noEmailItem.visible = survey.currentPage?.name === EMAIL_PAGE
      notMovingOutItem.visible =
        survey.currentPage?.name === BONDS_MOVE_OUT_PAGE
      // The review toggle lives on the submit page only; collapse the panel
      // whenever the user leaves, so it reopens closed next time.
      const onSubmit = survey.currentPage?.name === SUBMIT_PAGE
      reviewToggleItem.visible = onSubmit
      if (!onSubmit) setReviewOpen(false)
      survey.pageNextText = onWelcome ? "Let's get started" : 'Next'
      // The count follows the stepper: hidden wherever section is -1, i.e. on
      // the WELCOME and SUBMIT pages.
      pageCountItem.title = `Page ${p.page} of ${p.pageCount}`
      pageCountItem.visible = p.section >= 0
      setProgress({
        ...p,
        direction: goingForward.current ? 'forward' : 'back',
      })
      setNavigable(navigableSections(survey, visited))
    }

    // Send a per-page funnel event the first time each page is reached (so back
    // / forward navigation doesn't recount it).
    const reportPage = () => {
      const name = survey.currentPage?.name
      if (!name || !markStepReported(name)) return
      const sectionIdx = sectionIndexForPage(name)
      events.onFormStep({
        index: survey.currentPageNo,
        name,
        section: sectionIdx >= 0 ? SECTIONS[sectionIdx]?.label : undefined,
      })
    }

    syncPage()
    reportPage()

    const persist = () => persistState(survey, saver, visited, session)

    const onPageChanging: Parameters<
      typeof survey.onCurrentPageChanging.add
    >[0] = (_, options) => {
      goingForward.current = options.isGoingForward
      // A history-driven move (Back / Forward) must not re-run the forward-only
      // exit / side-effect logic or re-mark the page's questions as visited.
      if (suppressPush.current) return
      if (!options.isGoingForward) return
      const page = options.oldCurrentPage
      if (!page) return
      // Advancing off WELCOME ("Let's get started") begins the intake proper.
      if (page.name === WELCOME_PAGE && markFormBegun()) {
        events.onFormBegin()
      }
      const { answers, exit } = applyPageAdvance(survey, page, visited, saver)
      if (exit) {
        options.allow = false
        exitFired.current = true
        persist()
        // The blocked page change means onPageChanged never fires, so send the
        // answers - including the exit-triggering one - to the server now, or
        // staff can't tell an exited user from an abandoner.
        saver.schedulePatch(answers)
        saver.flush()
        events.onFormExit({ question: exit.question, route: exit.route })
        navigate(exit.route)
        return
      }
      persist()
    }

    const onPageChanged = () => {
      persist()
      const answers = serializeAnswers(survey, visited)
      saver.schedulePatch(answers)
      // Retry the submission create if the EMAIL-time one failed (a network
      // blip): without a submission id, PATCHes no-op and no partial
      // submission exists server-side, so abandonment reminders never fire.
      // create() is idempotent - a no-op once the id exists or a create is
      // already in flight.
      if (!saver.submissionId && answers.EMAIL) {
        saver.create(answers).catch(logException)
      }
      window.scrollTo(0, 0)
      syncPage()
      reportPage()
      const name = survey.currentPage?.name ?? null
      if (suppressPush.current || forwardReconcile.current) {
        // This change mirrors a Back / Forward - it is already in the history.
        suppressPush.current = false
        lastPage.current = name
      } else if (goingForward.current) {
        // Advancing to a page: give it its own history entry.
        recordPage(name)
      } else {
        // Going back via the survey's Previous button. If a prior form entry
        // exists in the browser history, step back to it (the reconcile effect
        // sees the survey is already here and leaves it be) so Back / Forward
        // stay in sync. At the history floor - e.g. a resumed session opened
        // straight onto this page - there is nothing to pop to, so replace the
        // current entry to stay in the form rather than navigating out of it.
        const state = window.history.state as { idx?: number } | null
        const idx = state?.idx
        lastPage.current = name
        if (idx != null && startIdx.current != null && idx > startIdx.current) {
          navigate(-1)
        } else {
          navigate(ROUTES.LANDING, {
            state: { page: name, session },
            replace: true,
          })
        }
      }
    }

    const onComplete: Parameters<typeof survey.onComplete.add>[0] = () => {
      attemptSubmit()
    }

    // The "Page x of y" nav item renders as an <input type="button"> (SurveyJS
    // has no non-button nav item). It is a read-only status, not a control, so
    // hide it from assistive tech - the named progressbar already conveys
    // progress - rather than announce a button that does nothing when
    // activated. Both attributes are required and verified against axe-core:
    // aria-hidden alone is an aria-hidden-focus violation because the input is
    // still focusable (disableTabStop only sets tabindex="-1"), and disabled
    // makes it non-focusable so the pair is clean. (No valid ARIA role turns an
    // input button into static text - the allowed role overrides are all
    // interactive.) SurveyJS re-renders the item on every page with the new
    // count, and the render timing differs between fresh, resumed and
    // page-change entry, so keep the attributes applied with an observer on the
    // survey container rather than chase individual render events.
    const container = document.querySelector('.intake-page')
    const syncNavAttributes = () => {
      const count = container?.querySelector<HTMLInputElement>(
        '.intake-page-count__text'
      )
      if (count && count.getAttribute('aria-hidden') !== 'true') {
        count.setAttribute('aria-hidden', 'true')
        count.disabled = true
      }
      // SurveyJS doesn't render an action's ariaExpanded onto the button, so
      // reflect the review panel's open state on the toggle element ourselves.
      const toggle = container?.querySelector('.intake-review__toggle')
      const expanded = String(reviewOpenRef.current)
      if (toggle && toggle.getAttribute('aria-expanded') !== expanded) {
        toggle.setAttribute('aria-expanded', expanded)
      }
    }
    const navObserver = container
      ? new MutationObserver(syncNavAttributes)
      : null
    navObserver?.observe(container as Node, {
      childList: true,
      subtree: true,
    })
    syncNavAttributes()

    // Flush the pending answers PATCH when the tab is closed or backgrounded:
    // the "answer, Next, close the tab" gesture would otherwise land inside
    // the debounce window and the last page's answers would never reach the
    // server (the request survives teardown via the PATCH's fetch keepalive).
    const flushOnPageHide = () => saver.flush()
    const flushOnHidden = () => {
      if (document.visibilityState === 'hidden') saver.flush()
    }
    window.addEventListener('pagehide', flushOnPageHide)
    document.addEventListener('visibilitychange', flushOnHidden)

    // An answer change (not just a page change) can change how far forward is
    // reachable - a branching answer reveals/hides pages, an exit answer
    // collapses the run - so recompute the clickable sections live.
    const onValueChanged = () =>
      setNavigable(navigableSections(survey, visited))

    survey.onCurrentPageChanging.add(onPageChanging)
    survey.onCurrentPageChanged.add(onPageChanged)
    survey.onComplete.add(onComplete)
    survey.onValueChanged.add(onValueChanged)
    return () => {
      window.removeEventListener('pagehide', flushOnPageHide)
      document.removeEventListener('visibilitychange', flushOnHidden)
      survey.onCurrentPageChanging.remove(onPageChanging)
      survey.onCurrentPageChanged.remove(onPageChanged)
      survey.onComplete.remove(onComplete)
      survey.onValueChanged.remove(onValueChanged)
      navObserver?.disconnect()
    }
  }, [survey, saver, visited, navigate, recordPage, session, attemptSubmit])

  // Keep the ghost toggle's label and aria-expanded in step with the panel.
  useEffect(() => {
    reviewOpenRef.current = reviewOpen
    const item = reviewToggle.current
    if (item) {
      item.title = reviewOpen ? 'Hide your answers' : 'Review your answers'
    }
    // aria-expanded isn't rendered from the action (see syncNavAttributes); set
    // it now, and the observer re-applies it after SurveyJS re-renders.
    document
      .querySelector('.intake-review__toggle')
      ?.setAttribute('aria-expanded', String(reviewOpen))
  }, [reviewOpen])

  return { progress, navigable, jumpToSection, editSection, reviewOpen }
}
