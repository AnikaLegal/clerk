import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { Model } from 'survey-core'
import { Survey } from 'survey-react-ui'

import { events } from '../analytics'
import { SectionProgress } from '../comps/SectionProgress'
import { ROUTES } from '../consts'
import { attachAddressAutocomplete } from '../form/address/attach'
import { getExitRoute } from '../form/exits'
import { markFormBegun, markStepReported, resetFunnel } from '../form/funnel'
import { restorePosition } from '../form/restore'
import { buildSurveyModel, WELCOME_PAGE } from '../form/model'
import { SubmissionSaver } from '../form/save'
import { serializeAnswers } from '../form/serialize'
import { runSideEffect } from '../form/side-effects'
import { clearState, loadState, saveState } from '../form/storage'
import { Answers } from '../form/types'
import { attachUploadHandler } from '../form/upload-handler'
import { logException } from '../utils'
import { setDocumentTitle } from './announce'
import {
  BONDS_MOVE_OUT_PAGE,
  EMAIL_PAGE,
  QUESTIONS_BY_NAME,
  SECTIONS,
  sectionIndexForPage,
  SUBMIT_PAGE,
} from '../questions'

interface FormState {
  survey: Model
  saver: SubmissionSaver
  visited: Set<string>
  // Id for this form-filling session, stamped into history entries (see the
  // reconcile effect).
  session: string
}

interface PageElement {
  name: string
  isVisible: boolean
}

// Direction of the last page change, used to slide the incoming page in from
// the side the user is travelling towards (forward -> from the right).
type Direction = 'forward' | 'back'

const isBlank = (value: unknown): boolean =>
  value === undefined ||
  value === null ||
  value === '' ||
  (Array.isArray(value) && value.length === 0)

// Names of the questions currently visible on a page, in display order. A
// hidden conditional question is excluded so its side effect / exit predicate
// isn't evaluated against an absent answer. Reads page.questions (not
// .elements) so questions nested inside panels are included.
const visibleNames = (page: { questions: PageElement[] }): string[] =>
  page.questions.filter((el) => el.isVisible).map((el) => el.name)

const setUpForm = (): FormState => {
  const stored = loadState()
  const survey = buildSurveyModel()
  const visited = new Set(stored.visited)
  survey.data = stored.data
  attachUploadHandler(survey)
  attachAddressAutocomplete(survey)

  // Carry the stored session across remounts (exit / no-email round trips,
  // reloads); mint a fresh one when there is no state (a new visitor, or Back
  // after a submit cleared it) so leftover history entries from the previous
  // session are recognised as stale.
  const session = stored.session ?? crypto.randomUUID()

  const saver = new SubmissionSaver(stored.submissionId, () => persist())
  const persist = () => {
    saveState({
      submissionId: saver.submissionId,
      data: survey.data,
      visited: [...visited],
      currentPage: survey.currentPage?.name ?? null,
      session,
    })
  }

  // Restore where the returning user re-enters the form (see restorePosition).
  restorePosition(survey, visited, stored.currentPage)

  // The WELCOME page's Next button reads "Let's get started"; every other page
  // keeps the default. Set it before the first render (syncPage maintains it on
  // later page changes) so a fresh visitor never sees the default label flash.
  survey.pageNextText =
    survey.currentPage?.name === WELCOME_PAGE ? "Let's get started" : 'Next'

  return { survey, saver, visited, session }
}

// State for the progress indicator. section is -1 on the WELCOME and SUBMIT
// pages, which sit outside the sectioned flow, so both the stepper and the
// "Page x of y" count hide there. page / pageCount drive the count over the
// question pages; the leading WELCOME page (visible page 0) and the trailing
// SUBMIT page are both excluded from the total, so the first question reads as
// "Page 1" and the count never includes the final agreement page.
const readProgress = (survey: Model) => {
  const name = survey.currentPage?.name
  return {
    name,
    section: name === SUBMIT_PAGE ? -1 : sectionIndexForPage(name),
    page: survey.currentPageNo,
    pageCount: survey.visiblePages.length - 2,
  }
}

export const FormPage = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { survey, saver, visited, session } = useMemo(setUpForm, [])
  const [progress, setProgress] = useState(() => ({
    ...readProgress(survey),
    direction: 'forward' as Direction,
  }))

  // Restore the form's title after a splash view (e.g. Go back from an exit
  // page) changed it. Matches the title the Django shell renders on load.
  // Focus is handled by the survey itself (autoFocusFirstQuestion).
  useEffect(() => {
    setDocumentTitle('Get free help')
  }, [])

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
    if (!page || !page.isVisible) return
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

  useEffect(() => {
    // A dedicated "I don't have an email address" navigation button that routes
    // to the no-email contact fallback. It sits in the survey's navigation bar
    // beside Previous / Next and is shown only while the email page is current.
    const noEmailItem = survey.addNavigationItem({
      id: 'nav-no-email',
      title: "I don't have an email address",
      innerCss: 'd-btn intake-btn-secondary',
      visible: false,
      action: () => {
        events.onFormExit({
          question: 'NO_EMAIL_BUTTON',
          route: ROUTES.NO_EMAIL,
        })
        navigate(ROUTES.NO_EMAIL)
      },
    })
    // Its sibling on the bonds move-out date page: users who are not moving
    // out exit to the bond-recovery resources page instead of answering the
    // (required) date question.
    const notMovingOutItem = survey.addNavigationItem({
      id: 'nav-not-moving-out',
      title: "I'm not moving out",
      innerCss: 'd-btn intake-btn-secondary',
      visible: false,
      action: () => {
        events.onFormExit({
          question: 'NOT_MOVING_OUT_BUTTON',
          route: ROUTES.INELIGIBLE_BOND_OUT_OF_SCOPE,
        })
        navigate(ROUTES.INELIGIBLE_BOND_OUT_OF_SCOPE)
      },
    })
    // A non-interactive "Page x of y" count rendered at the far right of the
    // navigation bar, vertically centred with the Previous / Next buttons. Its
    // wrapper is pushed right and its button styling stripped to plain text in
    // global.css; disableTabStop keeps it out of the keyboard tab order. A high
    // visibleIndex keeps it last so the right-push separates only it.
    const pageCountItem = survey.addNavigationItem({
      id: 'nav-page-count',
      title: '',
      css: 'intake-page-count',
      innerCss: 'intake-page-count__text',
      disableTabStop: true,
      visibleIndex: 1000,
      visible: false,
      action: () => {},
    })
    // Keep the per-page UI in sync with the current page: the no-email button's
    // visibility, the WELCOME page's "Let's get started" button label, the page
    // count, and the progress stepper's active section.
    const syncPage = () => {
      const p = readProgress(survey)
      const onWelcome = survey.currentPage?.name === WELCOME_PAGE
      noEmailItem.visible = survey.currentPage?.name === EMAIL_PAGE
      notMovingOutItem.visible =
        survey.currentPage?.name === BONDS_MOVE_OUT_PAGE
      survey.pageNextText = onWelcome ? "Let's get started" : 'Next'
      // The count follows the stepper: hidden wherever section is -1, i.e. on
      // the WELCOME and SUBMIT pages.
      pageCountItem.title = `Page ${p.page} of ${p.pageCount}`
      pageCountItem.visible = p.section >= 0
      setProgress({
        ...p,
        direction: goingForward.current ? 'forward' : 'back',
      })
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

    const persist = () => {
      saveState({
        submissionId: saver.submissionId,
        data: survey.data,
        visited: [...visited],
        currentPage: survey.currentPage?.name ?? null,
        session,
      })
    }

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
      const names = visibleNames(
        page as unknown as { questions: PageElement[] }
      )
      // Apply skip defaults for questions left blank (e.g. dependants -> 0)
      // and record every question on the page as passed.
      for (const name of names) {
        const question = QUESTIONS_BY_NAME[name]
        if (!question || question.type === 'DISPLAY') continue
        if (
          question.skipDefault !== undefined &&
          isBlank(survey.getValue(name))
        ) {
          survey.setValue(name, question.skipDefault)
        }
        visited.add(name)
      }
      const answers = serializeAnswers(survey, visited)
      // Fire each question's side effect, then check its exit, in page order.
      // The first exit that matches ejects the user (later questions on the
      // page are treated as not reached, as they would be one-per-page).
      for (const name of names) {
        runSideEffect(name, { answers, saver })
        const exit = getExitRoute(name, survey.data as Answers)
        if (exit) {
          options.allow = false
          exitFired.current = true
          persist()
          // The blocked page change means onPageChanged never fires, so send
          // the answers - including the exit-triggering one - to the server
          // now, or staff can't tell an exited user from an abandoner.
          saver.schedulePatch(answers)
          saver.flush()
          events.onFormExit({ question: name, route: exit })
          navigate(exit)
          return
        }
      }
      persist()
    }

    const onPageChanged = () => {
      persist()
      saver.schedulePatch(serializeAnswers(survey, visited))
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

    const onComplete: Parameters<typeof survey.onComplete.add>[0] = (
      _,
      options
    ) => {
      options.showSaveInProgress()
      const answers = serializeAnswers(survey, visited)
      saver
        .submit(answers)
        .then(() => {
          events.onFormComplete()
          clearState()
          resetFunnel()
          navigate(ROUTES.SUBMITTED)
        })
        .catch((error) => {
          logException(error)
          // Renders a message with a retry button that re-fires onComplete.
          options.showSaveError()
        })
    }

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

    survey.onCurrentPageChanging.add(onPageChanging)
    survey.onCurrentPageChanged.add(onPageChanged)
    survey.onComplete.add(onComplete)
    return () => {
      window.removeEventListener('pagehide', flushOnPageHide)
      document.removeEventListener('visibilitychange', flushOnHidden)
      survey.onCurrentPageChanging.remove(onPageChanging)
      survey.onCurrentPageChanged.remove(onPageChanged)
      survey.onComplete.remove(onComplete)
    }
  }, [survey, saver, visited, navigate, recordPage, session])

  return (
    <div
      className={
        progress.name === WELCOME_PAGE
          ? 'intake-form intake-form--welcome'
          : 'intake-form'
      }
    >
      {progress.section >= 0 && <SectionProgress current={progress.section} />}
      {/* The outer div clips the horizontal slide; the inner is re-keyed by page
          name so the direction-aware animation in global.css replays on every
          page change. The survey Model is stable across the remount (it lives in
          useMemo), so only the view is rebuilt. */}
      <div className="intake-page">
        <div
          key={progress.name}
          className={`intake-page__inner intake-page__inner--${progress.direction}`}
        >
          <Survey model={survey} />
        </div>
      </div>
    </div>
  )
}
