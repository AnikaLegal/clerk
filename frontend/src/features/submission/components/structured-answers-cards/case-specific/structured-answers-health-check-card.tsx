import { Anchor, CardProps } from '@mantine/core'
import { SubmissionAnswers } from 'api'
import React from 'react'
import { StructuredAnswersCard } from '../structured-answers-card'

export interface StructuredAnswersHealthCheckCardProps {
  answers: SubmissionAnswers
  card?: CardProps
}

export const StructuredAnswersHealthCheckCard = ({
  answers,
  card,
}: StructuredAnswersHealthCheckCardProps) => {
  if (!answers.topic_specific || !answers.topic_specific.HEALTH_CHECK) {
    return null
  }
  const healthCheck = answers.topic_specific.HEALTH_CHECK
  const data = [
    [
      {
        label: 'Support worker authority document(s)',
        value: healthCheck.support_worker_authority?.map((file, index) => (
          <>
            {index > 0 && ' | '}
            <Anchor key={file.url} href={file.url} target="_blank">
              {file.name}
            </Anchor>
          </>
        )),
      },
      {
        label: 'Tenancy document(s)',
        value: healthCheck.tenancy_documents?.map((file, index) => (
          <>
            {index > 0 && ' | '}
            <Anchor key={file.url} href={file.url} target="_blank">
              {file.name}
            </Anchor>
          </>
        )),
      },
    ],
  ]
  return (
    <StructuredAnswersCard
      title="Health check information"
      data={data}
      card={card}
    />
  )
}
