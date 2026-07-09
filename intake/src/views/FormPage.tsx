import { useEffect, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { Model } from 'survey-core'
import { Survey } from 'survey-react-ui'

import { events } from '../analytics'
import { Header } from '../comps/Header'
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
import { QUESTIONS_BY_NAME } from '../questions'

interface FormState {
  survey: Model
  saver: SubmissionSaver
  visited: Set<string>
}

const isBlank = (value: unknown): boolean =>
  value === undefined ||
  value === null ||
  value === '' ||
  (Array.isArray(value) && value.length === 0)

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
      currentQuestion: survey.currentPage?.name ?? null,
    })
  }

  // Restore position: the stored current question, or (after a resume, or
  // when the stored question is no longer visible) the first question on
  // the active branch the user hasn't passed yet.
  let restored = false
  if (stored.currentQuestion) {
    const page = survey.getPageByName(stored.currentQuestion)
    if (page && page.isVisible) {
      survey.currentPage = page
      restored = true
    }
  }
  if (!restored && visited.size > 0) {
    const nextPage = survey.pages.find((page) => {
      const question = QUESTIONS_BY_NAME[page.name]
      return (
        page.isVisible &&
        question &&
        question.type !== 'DISPLAY' &&
        !visited.has(page.name)
      )
    })
    if (nextPage) {
      survey.currentPage = nextPage
    }
  }

  return { survey, saver, visited }
}

export const FormPage = () => {
  const navigate = useNavigate()
  const { survey, saver, visited } = useMemo(setUpForm, [])

  useEffect(() => {
    const persist = () => {
      saveState({
        submissionId: saver.submissionId,
        data: survey.data,
        visited: [...visited],
        currentQuestion: survey.currentPage?.name ?? null,
      })
    }

    const onPageChanging: Parameters<
      typeof survey.onCurrentPageChanging.add
    >[0] = (_, options) => {
      if (!options.isGoingForward) return
      const page = options.oldCurrentPage
      if (!page) return
      const question = QUESTIONS_BY_NAME[page.name]
      // Apply skip defaults for questions left blank (e.g. dependants -> 0).
      if (
        question?.skipDefault !== undefined &&
        isBlank(survey.getValue(page.name))
      ) {
        survey.setValue(page.name, question.skipDefault)
      }
      visited.add(page.name)
      const answers = serializeAnswers(survey, visited)
      runSideEffect(page.name, { answers, saver })
      persist()
      const exit = getExitRoute(page.name, survey.data as Answers)
      if (exit) {
        options.allow = false
        persist()
        navigate(exit)
      }
    }

    const onPageChanged = () => {
      persist()
      saver.schedulePatch(serializeAnswers(survey, visited))
      window.scrollTo(0, 0)
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
  }, [survey, saver, visited, navigate])

  return (
    <div className="intake-form">
      <Header />
      <Survey model={survey} />
    </div>
  )
}
