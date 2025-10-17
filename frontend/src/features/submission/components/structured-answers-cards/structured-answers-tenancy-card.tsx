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
  if (!answers.tenancy) {
    return null
  }
  const tenancy = answers.tenancy
  const data = [
    [
      { label: 'Address', value: tenancy.address },
      { label: 'Suburb', value: tenancy.suburb },
      { label: 'Postcode', value: tenancy.postcode },
    ],
    [
      { label: 'Start date', value: tenancy.start_date },
      {
        label: 'Is client on lease?',
        value: tenancy.is_on_lease?.label,
      },
      {
        label: 'Rental circumstances',
        value: tenancy.rental_circumstances?.label,
      },
    ],
    [{ label: 'Weekly rent', value: answers.issue?.weekly_rent }],
  ]
  return <StructuredAnswersCard title="Tenancy" data={data} card={card} />
}
