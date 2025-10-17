import { Card, CardProps, Group, Text } from '@mantine/core'
import { IconExclamationCircle } from '@tabler/icons-react'
import { SubmissionAnswers } from 'api'
import React from 'react'
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
  return (
    <Card {...card}>
      {data ? (
        <>
          <StructuredAnswersCaseCard answers={data} />
          <StructuredAnswersClientCard answers={data} card={{ mt: 'md' }} />
          <StructuredAnswersSupportWorkerCard
            answers={data}
            card={{ mt: 'md' }}
          />
          <StructuredAnswersTenancyCard answers={data} card={{ mt: 'md' }} />
          <StructuredAnswersAgentCard answers={data} card={{ mt: 'md' }} />
          <StructuredAnswersLandlordCard answers={data} card={{ mt: 'md' }} />
        </>
      ) : (
        <Group justify="center" gap="xs" m="sm">
          <IconExclamationCircle />
          <Text>Could not structure submission data</Text>
        </Group>
      )}
    </Card>
  )
}
