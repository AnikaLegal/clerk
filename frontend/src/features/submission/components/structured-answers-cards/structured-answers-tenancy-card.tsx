import { CardProps } from '@mantine/core'
import { SubmissionAnswers } from 'api'
import React from 'react'
import { StructuredAnswersCard } from './structured-answers-card'

export interface StructuredAnswersTenancyCardProps {
  answers: SubmissionAnswers
  card?: CardProps
}

export const StructuredAnswersTenancyCard = ({
  answers,
  card,
}: StructuredAnswersTenancyCardProps) => {
  if (!answers.tenancy && !answers.issue?.weekly_rent) {
    return null
  }
  const data = [
    [
      { label: 'Address', value: answers.tenancy?.address },
      { label: 'Suburb', value: answers.tenancy?.suburb },
      { label: 'Postcode', value: answers.tenancy?.postcode },
    ],
    [
      { label: 'Start date', value: answers.tenancy?.start_date },
      {
        label: 'Is client on lease?',
        value: answers.tenancy?.is_on_lease?.label,
      },
      {
        label: 'Rental circumstances',
        value: answers.tenancy?.rental_circumstances?.label,
      },
    ],
    [{ label: 'Weekly rent', value: answers.issue?.weekly_rent }],
  ]
  return <StructuredAnswersCard title="Tenancy" data={data} card={card} />
}
