import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { Model } from 'survey-core'
import { Survey } from 'survey-react-ui'

import { events } from '../analytics'
import { SectionProgress } from '../comps/SectionProgress'
import { ROUTES } from '../consts'
import { getExitRoute } from '../form/exits'
import { buildSurveyModel, WELCOME_PAGE } from '../form/model'
import { SubmissionSaver } from '../form/save'
import { serializeAnswers } from '../form/serialize'
import { runSideEffect } from '../form/side-effects'
import { clearState, loadState, saveState } from '../form/storage'
import { Answers } from '../form/types'
import { attachUploadHandler } from '../form/upload-handler'
import { logException } from '../utils'
import { EMAIL_PAGE, QUESTIONS_BY_NAME, sectionIndexForPage } from '../questions'

interface FormState {
  survey: Model
  saver: SubmissionSaver
  visited: Set<string>
}

interface PageElement {
  name: string
  isVisible: boolean
}

const isBlank = (value: unknown): boolean =>
  value === undefined ||
  value === null ||
  value === '' ||
  (Array.isArray(value) && value.length === 0)

// Names of the questions currently visible on a page, in display order. A
// hidden conditional question is excluded so its side effect / exit predicate
// isn't evaluated against an absent answer.
const visibleNames = (page: { elements: PageElement[] }): string[] =>
  page.elements.filter((el) => el.isVisible).map((el) => el.name)

const setUpForm = (): FormState => {
  const stored = loadState()
  const survey = buildSurveyModel()
  const visited = new Set(stored.visited)
  survey.data = stored.data
  attachUploadHandler(survey)

  const saver = new SubmissionSaver(stored.submissionId, () => persist())
  const persist = () => {
    saveState({
      submissionId: saver.submissionId,
      data: survey.data,
      visited: [...visited],
      currentPage: survey.currentPage?.name ?? null,
    })
  }

  // Restore position: the stored current page, or (after a resume, or when
  // the stored page is no longer visible) the first visible page that still
  // has an unanswered question the user hasn't passed. A brand-new visitor has
  // no stored position and opens on the leading WELCOME page.
  let restored = false
  if (stored.currentPage) {
    const page = survey.getPageByName(stored.currentPage)
    if (page && page.isVisible) {
      survey.currentPage = page
      restored = true
    }
  }
  if (!restored && visited.size > 0) {
    const nextPage = survey.pages.find(
      (page) =>
        page.isVisible &&
        (page.elements as unknown as PageElement[]).some((el) => {
          const question = QUESTIONS_BY_NAME[el.name]
          return (
            el.isVisible &&
            question &&
            question.type !== 'DISPLAY' &&
            !visited.has(el.name)
          )
        })
    )
    if (nextPage) {
      survey.currentPage = nextPage
    }
  }

  // The WELCOME page's Next button reads "Let's get started"; every other page
  // keeps the default. Set it before the first render (syncPage maintains it on
  // later page changes) so a fresh visitor never sees the default label flash.
  survey.pageNextText =
    survey.currentPage?.name === WELCOME_PAGE ? "Let's get started" : 'Next'

  return { survey, saver, visited }
}

// State for the progress stepper. section is -1 on the WELCOME page (which is
// not part of any section, so the stepper hides there); page / pageCount drive
// the "Page x of y" count over the question pages, excluding WELCOME (visible
// page 0) so the first question reads as "Page 1".
const readProgress = (survey: Model) => ({
  section: sectionIndexForPage(survey.currentPage?.name),
  page: survey.currentPageNo,
  pageCount: survey.visiblePages.length - 1,
})

export const FormPage = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { survey, saver, visited } = useMemo(setUpForm, [])
  const [progress, setProgress] = useState(() => readProgress(survey))

  // Browser history <-> survey page sync, so the browser Back / Forward buttons
  // move between the survey's pages instead of leaving the form. Each page gets
  // its own history entry carrying its name in location.state. lastPage tracks
  // the page recorded at the top of the stack; suppressPush marks a survey page
  // change that is itself mirroring a Back / Forward, so it isn't re-recorded.
  const lastPage = useRef<string | null>(null)
  const suppressPush = useRef(false)
  // Direction of the page change in progress, captured in onCurrentPageChanging
  // (which carries it) and read in onCurrentPageChanged (which does not), so a
  // backward move via the survey's Previous button steps back through history
  // rather than pushing a duplicate entry.
  const goingForward = useRef(true)
  // Ensures the startIntake analytics event fires only once, even if the user
  // navigates back to WELCOME and forward again.
  const startFired = useRef(false)

  const recordPage = useCallback(
    (name: string | null | undefined) => {
      if (!name || lastPage.current === name) return
      // The first real page replaces the initial entry in place (so Back from
      // it leaves the form); later pages push a new entry to move forward over.
      navigate(ROUTES.LANDING, {
        state: { page: name },
        replace: lastPage.current === null,
      })
      lastPage.current = name
    },
    [navigate]
  )

  // Mirror a browser Back / Forward (location change) onto the survey: move it
  // to the page named in the history entry we landed on.
  useEffect(() => {
    const target = (location.state as { page?: string } | null)?.page
    // lastPage null means the initial entry has not been stamped yet (see the
    // mount effect below); ignore any page named in a leftover history entry
    // (e.g. returning via Back after a submit cleared the saved state) until
    // then, so the survey opens where setUpForm placed it, not a stale page.
    if (!target || lastPage.current === null || lastPage.current === target)
      return
    if (survey.currentPage?.name === target) {
      lastPage.current = target
      return
    }
    const page = survey.getPageByName(target)
    if (page && page.isVisible) {
      suppressPush.current = true
      lastPage.current = target
      survey.currentPage = page
    }
  }, [location, survey])

  // Stamp the initial history entry for the page the survey opens on (WELCOME
  // for a fresh visitor, or the restored page when resuming). Runs once on
  // mount - recordPage / survey are stable for the component's life.
  useEffect(() => {
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
      action: () => navigate(ROUTES.NO_EMAIL),
    })
    // Keep the per-page UI in sync with the current page: the no-email button's
    // visibility, the WELCOME page's "Let's get started" button label, and the
    // progress stepper's active section.
    const syncPage = () => {
      const onWelcome = survey.currentPage?.name === WELCOME_PAGE
      noEmailItem.visible = survey.currentPage?.name === EMAIL_PAGE
      survey.pageNextText = onWelcome ? "Let's get started" : 'Next'
      setProgress(readProgress(survey))
    }
    syncPage()

    const persist = () => {
      saveState({
        submissionId: saver.submissionId,
        data: survey.data,
        visited: [...visited],
        currentPage: survey.currentPage?.name ?? null,
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
      if (page.name === WELCOME_PAGE && !startFired.current) {
        startFired.current = true
        events.onStartIntake()
      }
      const names = visibleNames(page as unknown as { elements: PageElement[] })
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
          persist()
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
      const name = survey.currentPage?.name ?? null
      if (suppressPush.current) {
        // This change mirrors a Back / Forward - it is already in the history.
        suppressPush.current = false
        lastPage.current = name
      } else if (goingForward.current) {
        // Advancing to a page: give it its own history entry.
        recordPage(name)
      } else {
        // Going back via the survey's Previous button: step back through the
        // browser history to this page's existing entry (the reconcile effect
        // sees the survey is already here and leaves it be), rather than
        // pushing a duplicate that would desync the Back / Forward buttons.
        lastPage.current = name
        navigate(-1)
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
          events.onFinishIntake()
          clearState()
          navigate(ROUTES.SUBMITTED)
        })
        .catch((error) => {
          logException(error)
          // Renders a message with a retry button that re-fires onComplete.
          options.showSaveError()
        })
    }

    survey.onCurrentPageChanging.add(onPageChanging)
    survey.onCurrentPageChanged.add(onPageChanged)
    survey.onComplete.add(onComplete)
    return () => {
      survey.onCurrentPageChanging.remove(onPageChanging)
      survey.onCurrentPageChanged.remove(onPageChanged)
      survey.onComplete.remove(onComplete)
    }
  }, [survey, saver, visited, navigate, recordPage])

  return (
    <div className="intake-form">
      {progress.section >= 0 && (
        <SectionProgress
          current={progress.section}
          page={progress.page}
          pageCount={progress.pageCount}
        />
      )}
      <Survey model={survey} />
    </div>
  )
}
