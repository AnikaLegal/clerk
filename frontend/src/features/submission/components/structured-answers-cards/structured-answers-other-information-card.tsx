import { CardProps } from '@mantine/core'
import { SubmissionAnswers } from 'api'
import React from 'react'
import { StructuredAnswersCard } from './structured-answers-card'

export interface StructuredAnswersOtherInformationCardProps {
  answers: SubmissionAnswers
  card?: CardProps
}

export const StructuredAnswersOtherInformationCard = ({
  answers,
  card,
}: StructuredAnswersOtherInformationCardProps) => {
  if (!answers.issue) {
    return null
  }
  const issue = answers.issue

  const data = [
    [
      { label: 'Referrer type', value: issue?.referrer_type?.label },
      { label: 'Referrer', value: issue?.referrer },
    ],
  ]
  return (
    <StructuredAnswersCard title="Other information" data={data} card={card} />
  )
}
