import { Anchor, CardProps } from '@mantine/core'
import { SubmissionAnswers } from 'api'
import React from 'react'
import { StructuredAnswersCard } from '../structured-answers-card'

export interface StructuredAnswersRentReductionCardProps {
  answers: SubmissionAnswers
  card?: CardProps
}

export const StructuredAnswersRentReductionCard = ({
  answers,
  card,
}: StructuredAnswersRentReductionCardProps) => {
  if (!answers.topic_specific || !answers.topic_specific.RENT_REDUCTION) {
    return null
  }
  const rentReduction = answers.topic_specific.RENT_REDUCTION
  const data = [
    [
      { label: 'Issues', value: rentReduction.issues?.join(' | ') },
      { label: 'Issue description', value: rentReduction.issue_description },
      {
        label: 'Issue photo(s)',
        value: rentReduction.issue_photos?.map((file, index) => (
          <>
            {index > 0 && ' | '}
            <Anchor key={file.url} href={file.url} target="_blank">
              {file.name}
            </Anchor>
          </>
        )),
      },
      { label: 'Problem start date', value: rentReduction.issue_start },
      {
        label: 'Is NTV issued?',
        value: rentReduction.is_notice_to_vacate?.label,
      },
      {
        label: 'NTV document',
        value: rentReduction.notice_to_vacate?.map((file, index) => (
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
      title="Rent reduction information"
      data={data}
      card={card}
    />
  )
}
