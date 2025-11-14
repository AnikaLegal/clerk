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
  if (
    !answers.client &&
    !answers.issue?.weekly_income &&
    !answers.issue?.employment_status
  ) {
    return null
  }
  const data = [
    [
      { label: 'First name', value: answers.client?.first_name },
      { label: 'Last name', value: answers.client?.last_name },
      { label: 'Preferred name', value: answers.client?.preferred_name },
      { label: 'Gender', value: answers.client?.gender },
      { label: 'Date of birth', value: answers.client?.date_of_birth },
    ],
    [
      { label: 'Email', value: answers.client?.email },
      { label: 'Phone number', value: answers.client?.phone_number },
      {
        label: 'Call times',
        value: answers.client?.call_times
          ?.map(({ label }) => label)
          .join(' | '),
      },
    ],
    [
      { label: 'Eligibility notes', value: answers.client?.eligibility_notes },
      {
        label: 'Eligibility circumstances',
        value: answers.client?.eligibility_circumstances
          ?.map(({ label }) => label)
          .join(' | '),
      },
      {
        label: 'Special circumstances (legacy)',
        value: answers.client?.special_circumstances
          ?.map(({ label }) => label)
          .join(' | '),
      },
      {
        label: 'Is on Centrelink?',
        value: answers.client?.centrelink_support?.label,
      },
      {
        label: 'Number of dependents',
        value: answers.client?.number_of_dependents,
      },
      { label: 'Primary language', value: answers.client?.primary_language },
      {
        label: 'Requires an interpreter?',
        value: answers.client?.requires_interpreter?.label,
      },
      {
        label: 'Is Aboriginal or Torres Strait Islander?',
        value: answers.client?.is_aboriginal_or_torres_strait_islander?.label,
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
