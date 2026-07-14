import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Model } from 'survey-core'
import { Survey } from 'survey-react-ui'

import { events } from '../analytics'
import { SectionProgress } from '../comps/SectionProgress'
import { ROUTES } from '../consts'
import { getExitRoute } from '../form/exits'
import { buildSurveyModel } from '../form/model'
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

  // A returning or resuming visitor (with stored progress) skips the start
  // page and picks up where they left off; a brand-new visitor stays on the
  // start page until they press Start. Leaving the start page must happen
  // before restoring a position, as currentPage only tracks real pages once
  // the survey is running. This runs before onStarted is wired up in the
  // effect below, so restoring here does not fire the startIntake event.
  if (visited.size > 0 || stored.currentPage) {
    survey.start()
  }

  // Restore position: the stored current page, or (after a resume, or when
  // the stored page is no longer visible) the first visible page that still
  // has an unanswered question the user hasn't passed.
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

  return { survey, saver, visited }
}

// The section shown in the progress stepper, or -1 while the welcome start page
// is up (currentPage skips the start page, so also guard on isShowStartingPage).
const currentSection = (survey: Model): number =>
  survey.isShowStartingPage ? -1 : sectionIndexForPage(survey.currentPage?.name)

export const FormPage = () => {
  const navigate = useNavigate()
  const { survey, saver, visited } = useMemo(setUpForm, [])
  const [section, setSection] = useState(() => currentSection(survey))

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
    // visibility and the progress stepper's active section.
    const syncPage = () => {
      noEmailItem.visible = survey.currentPage?.name === EMAIL_PAGE
      setSection(currentSection(survey))
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
      if (!options.isGoingForward) return
      const page = options.oldCurrentPage
      if (!page) return
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
    }

    // Fired when the user presses Start on the start page. A restored session
    // leaves the start page in setUpForm (before this handler is attached), so
    // this only fires for a genuine fresh start.
    const onStarted = () => {
      events.onStartIntake()
      syncPage()
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

    survey.onStarted.add(onStarted)
    survey.onCurrentPageChanging.add(onPageChanging)
    survey.onCurrentPageChanged.add(onPageChanged)
    survey.onComplete.add(onComplete)
    return () => {
      survey.onStarted.remove(onStarted)
      survey.onCurrentPageChanging.remove(onPageChanging)
      survey.onCurrentPageChanged.remove(onPageChanged)
      survey.onComplete.remove(onComplete)
    }
  }, [survey, saver, visited, navigate])

  return (
    <div className="intake-form">
      {section >= 0 && <SectionProgress current={section} />}
      <Survey model={survey} />
    </div>
  )
}
