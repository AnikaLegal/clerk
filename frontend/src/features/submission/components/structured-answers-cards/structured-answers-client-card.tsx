import { CardProps } from '@mantine/core'
import { SubmissionAnswers } from 'api'
import React from 'react'
import { StructuredAnswersCard } from './structured-answers-card'

export interface StructuredAnswersClientCardProps {
  answers: SubmissionAnswers
  card?: CardProps
}

export const StructuredAnswersClientCard = ({
  answers,
  card,
}: StructuredAnswersClientCardProps) => {
  if (!answers.client) {
    return null
  }
  const client = answers.client
  const data = [
    [
      { label: 'First name', value: client.first_name },
      { label: 'Last name', value: client.last_name },
      { label: 'Preferred name', value: client.preferred_name },
      { label: 'Gender', value: client.gender },
      { label: 'Date of birth', value: client.date_of_birth },
    ],
    [
      { label: 'Email', value: client.email },
      { label: 'Phone number', value: client.phone_number },
      {
        label: 'Call times',
        value: client.call_times?.map(({ label }) => label).join(' | '),
      },
    ],
    [
      { label: 'Eligibility notes', value: client.eligibility_notes },
      {
        label: 'Eligibility circumstances',
        value: client.eligibility_circumstances
          ?.map(({ label }) => label)
          .join(' | '),
      },
      {
        label: 'Special circumstances (legacy)',
        value: client.special_circumstances
          ?.map(({ label }) => label)
          .join(' | '),
      },
      { label: 'Is on Centrelink?', value: client.centrelink_support?.label },
      { label: 'Number of dependents', value: client.number_of_dependents },
      { label: 'Primary language', value: client.primary_language },
      {
        label: 'Requires an interpreter?',
        value: client.requires_interpreter?.label,
      },
      {
        label: 'Is Aboriginal or Torres Strait Islander?',
        value: client.is_aboriginal_or_torres_strait_islander?.label,
      },
    ],
    [
      { label: 'Weekly income', value: answers.issue?.weekly_income },
      {
        label: 'Employment status',
        value: answers.issue?.employment_status
          ?.map(({ label }) => label)
          .join(' | '),
      },
    ],
  ]
  return <StructuredAnswersCard title="Client" data={data} card={card} />
}
