import React from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import styled from 'styled-components'

import { ROUTES } from 'intake/consts'
import {
  FadeFooter,
  Text,
  FadeInOut,
  ANIMATION_TIME,
  Navbar,
} from 'intake/design'
import {
  useScrollTop,
  waitSeconds,
  loadFormData,
  storeFormData,
} from 'intake/utils'
import type { Field, Data } from 'intake/types'
import { QUESTIONS, STAGES } from 'intake/questions'
import { FORM_FIELDS } from 'intake/components/fields'
import { api } from 'intake/api'

const INITIAL_DATA = {
  ISSUES: 'HEALTH_CHECK', // Always health check type case.
  IS_ON_LEASE: 'YES', // Always assumed to be true for health check cases.
}

export const FormView = () => {
  useScrollTop()
  const [data, setData] = React.useState<Data>(loadFormData() || INITIAL_DATA)
  const [question, qIdx] = useQuestion(data)
  const { onBack, onNext, onSkip, isFormVisible } = useFormNavigation(
    question,
    qIdx,
    data,
    setData
  )

  if (!question) return null

  // Find the field we should use to ask the question.
  const FormField = FORM_FIELDS[question.type]
  if (!FormField) return null

  const value = data[question.name]
  console.log('Form data', data)
  console.log('Current question', question.name, value)

  // User enters some data.
  const onChange = (v) => {
    setData((d) => ({ ...d, [question.name]: v }))
  }
  // User tries to upload a file
  const onUpload = (file: File) => api.intake.upload(file)

  return (
    <>
      <FormEl>
        <Navbar current={question.stage} onBack={onBack} steps={STAGES} />
        <FadeInOut visible={isFormVisible}>
          <FormField
            key={question.name}
            onNext={onNext}
            onSkip={onSkip}
            field={question}
            data={data}
            value={value}
            onChange={onChange}
            onUpload={onUpload}
          >
            <Text.Header>{question.Prompt}</Text.Header>
            {question.Help && <Text.Body>{question.Help}</Text.Body>}
          </FormField>
        </FadeInOut>
      </FormEl>
      {isFormVisible && <FadeFooter />}
    </>
  )
}

const FormEl = styled.div`
  overflow-x: hidden;
`

// Find the next valid question to ask.
const useQuestion = (data: Data): [Field | null, number] => {
  const navigate = useNavigate()
  const params = useParams()
  const qIdx = Number(params.qIdx)
  const [question, setQuestion] = React.useState<Field | null>(null)
  React.useEffect(() => {
    let nextQuestion = null
    const prevQs = []
    for (let q of QUESTIONS) {
      // Ignore fields that do not have their "ask condition" met.
      if (q.askCondition && !q.askCondition(data)) {
        continue
      }
      // Ignore fields that have been answered or skipped.
      if (typeof data[q.name] !== 'undefined') {
        prevQs.push(q)
        continue
      }
      nextQuestion = q
      break
    }
    if (qIdx >= 0 && qIdx < prevQs.length) {
      // User is looking at an answered question
      setQuestion(prevQs[qIdx])
    } else if (qIdx == prevQs.length && nextQuestion) {
      // User is looking at the next question
      setQuestion(nextQuestion)
    } else {
      // User is looking at some garbage qIdx, send them to next question
      const newIdx = prevQs.length
      const route = ROUTES.FORM.replace(':qIdx', String(newIdx))
      navigate(route)
    }
  }, [qIdx])

  return [question, qIdx]
}

const useFormNavigation = (
  question: Field | null,
  qIdx: number,
  data: Data,
  setData: any
) => {
  const navigate = useNavigate()

  // Handle form animation transition in / out
  const [isFormVisible, setIsFormVisible] = React.useState(false)
  React.useEffect(() => {
    setIsFormVisible(true)
  }, [])

  // Handle next page event
  const [isNavigateNext, setIsNavigateNext] = React.useState(false)
  const [isNavigateSkip, setIsNavigateSkip] = React.useState(false)
  React.useEffect(() => {
    if ((!isNavigateNext && !isNavigateSkip) || !question) return
    const latestData = { ...data }
    if (isNavigateSkip) {
      // Handle skip
      latestData[question.name] = null
      setData(latestData)
      setIsNavigateSkip(false)
    } else if (typeof latestData[question.name] === 'undefined') {
      // Set non-required fields to null if no answer was given.
      latestData[question.name] = null
      setData(latestData)
    }
    // Save form data to local storage when question answered
    storeFormData(latestData)
    // Run question side effects.
    const effectPromise = question.effect
      ? question.effect(latestData)
      : Promise.resolve()
    // Trigger animation.
    effectPromise.then(async (effectNextUrl) => {
      if (effectNextUrl) {
        navigate(effectNextUrl)
      } else {
        setIsFormVisible(false)
        await waitSeconds(ANIMATION_TIME / 2000)
        const route = ROUTES.FORM.replace(':qIdx', String(qIdx + 1))
        navigate(route)
        setIsNavigateNext(false)
        setIsFormVisible(true)
      }
    })
  }, [isNavigateNext, isNavigateSkip])

  const onBack = () => {
    if (qIdx > 0) {
      const route = ROUTES.FORM.replace(':qIdx', String(qIdx - 1))
      navigate(route)
    } else {
      navigate(ROUTES.LANDING)
    }
  }
  // Progress form to next question
  const onNext = (e) => {
    e?.preventDefault() // Don't submit HTML form.
    setIsNavigateNext(true)
  }

  const onSkip = (e) => {
    e?.preventDefault()
    setIsNavigateSkip(true)
  }

  return { onBack, onNext, onSkip, isFormVisible }
}
