import { CardProps } from '@mantine/core'
import { SubmissionAnswers } from 'api'
import React from 'react'
import { StructuredAnswersCard } from './structured-answers-card'

export interface StructuredAnswersLandlordCardProps {
  answers: SubmissionAnswers
  card?: CardProps
}

export const StructuredAnswersLandlordCard = ({
  answers,
  card,
}: StructuredAnswersLandlordCardProps) => {
  if (!answers.tenancy?.landlord) {
    return null
  }
  const landlord = answers.tenancy.landlord
  const data = [
    [
      { label: 'Name', value: landlord.name },
      { label: 'Email', value: landlord.email },
      { label: 'Address', value: landlord.address },
      { label: 'Phone number', value: landlord.phone_number },
    ],
  ]
  return <StructuredAnswersCard title="Landlord" data={data} card={card} />
}
