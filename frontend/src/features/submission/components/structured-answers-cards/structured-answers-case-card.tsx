import { CardProps } from '@mantine/core'
import { SubmissionAnswers } from 'api'
import React from 'react'
import { StructuredAnswersCard } from './structured-answers-card'

export interface StructuredAnswersCaseCardProps {
  answers: SubmissionAnswers
  card?: CardProps
}

export const StructuredAnswersCaseCard = ({
  answers,
  card,
}: StructuredAnswersCaseCardProps) => {
  if (!answers.issue) {
    return null
  }
  const issue = answers.issue
  const data = [
    [
      {
        label: 'Topic(s)',
        value: issue.issues?.map(({ label }) => label).join(' | '),
      },
      { label: 'Referrer type', value: issue.referrer_type?.label },
      { label: 'Referrer', value: issue.referrer },
    ],
  ]
  return <StructuredAnswersCard title="Case" data={data} card={card} />
}
