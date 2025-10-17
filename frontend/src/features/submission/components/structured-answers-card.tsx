import { Card, CardProps, Center } from '@mantine/core'
import { SubmissionAnswers } from 'api'
import React from 'react'
import { EmptyState } from './answers-display-states'
import {
  StructuredAnswersAgentCard,
  StructuredAnswersCaseCard,
  StructuredAnswersClientCard,
  StructuredAnswersLandlordCard,
  StructuredAnswersSupportWorkerCard,
  StructuredAnswersTenancyCard,
} from './structured-answers-cards'

export interface SubmissionStructuredAnswersCardProps {
  data: SubmissionAnswers | null
  card?: CardProps
}

export const SubmissionStructuredAnswersCard = ({
  data,
  card,
}: SubmissionStructuredAnswersCardProps) => {
  if (!data) {
    return (
      <Center>
        <EmptyState />
      </Center>
    )
  }

  return (
    <Card {...card}>
      <StructuredAnswersCaseCard answers={data} />
      <StructuredAnswersClientCard answers={data} card={{ mt: 'md' }} />
      <StructuredAnswersSupportWorkerCard answers={data} card={{ mt: 'md' }} />
      <StructuredAnswersTenancyCard answers={data} card={{ mt: 'md' }} />
      <StructuredAnswersAgentCard answers={data} card={{ mt: 'md' }} />
      <StructuredAnswersLandlordCard answers={data} card={{ mt: 'md' }} />
    </Card>
  )
}
