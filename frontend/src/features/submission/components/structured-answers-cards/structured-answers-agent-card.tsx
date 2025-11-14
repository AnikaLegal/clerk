import { CardProps } from '@mantine/core'
import { SubmissionAnswers } from 'api'
import React from 'react'
import { StructuredAnswersCard } from './structured-answers-card'

export interface StructuredAnswersAgentCardProps {
  answers: SubmissionAnswers
  card?: CardProps
}

export const StructuredAnswersAgentCard = ({
  answers,
  card,
}: StructuredAnswersAgentCardProps) => {
  if (!answers.tenancy?.agent) {
    return null
  }
  const agent = answers.tenancy.agent
  const data = [
    [
      { label: 'Name', value: agent.name },
      { label: 'Email', value: agent.email },
      { label: 'Address', value: agent.address },
      { label: 'Phone number', value: agent.phone_number },
    ],
  ]
  return <StructuredAnswersCard title="Agent" data={data} card={card} />
}
