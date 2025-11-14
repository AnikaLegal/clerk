import { CardProps } from '@mantine/core'
import { SubmissionAnswers } from 'api'
import React from 'react'
import { StructuredAnswersCard } from '../structured-answers-card'

export interface StructuredAnswersOtherCaseCardProps {
  answers: SubmissionAnswers
  card?: CardProps
}

export const StructuredAnswersOtherCaseCard = ({
  answers,
  card,
}: StructuredAnswersOtherCaseCardProps) => {
  if (!answers.topic_specific || !answers.topic_specific.OTHER) {
    return null
  }
  const other = answers.topic_specific.OTHER
  const data = [
    [{ label: 'Issue description', value: other.issue_description }],
  ]
  return (
    <StructuredAnswersCard
      title="Other case information"
      data={data}
      card={card}
    />
  )
}
