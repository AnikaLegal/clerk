import { CardProps } from '@mantine/core'
import { SubmissionAnswers } from 'api'
import React from 'react'
import { StructuredAnswersCard } from './structured-answers-card'

export interface StructuredAnswersSupportWorkerCardProps {
  answers: SubmissionAnswers
  card?: CardProps
}

export const StructuredAnswersSupportWorkerCard = ({
  answers,
  card,
}: StructuredAnswersSupportWorkerCardProps) => {
  if (!answers.issue?.support_worker) {
    return null
  }
  const supportWorker = answers.issue.support_worker
  const data = [
    [
      { label: 'Name', value: supportWorker.name },
      { label: 'Email', value: supportWorker.email },
      { label: 'Address', value: supportWorker.address },
      { label: 'Phone number', value: supportWorker.phone_number },
      {
        label: 'Contact preferences',
        value: supportWorker.support_contact_preferences?.label,
      },
    ],
  ]
  return (
    <StructuredAnswersCard title="Support worker" data={data} card={card} />
  )
}
