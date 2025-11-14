import { Anchor, CardProps } from '@mantine/core'
import { SubmissionAnswers } from 'api'
import React from 'react'
import { StructuredAnswersCard } from '../structured-answers-card'

export interface StructuredAnswersRepairsCardProps {
  answers: SubmissionAnswers
  card?: CardProps
}

export const StructuredAnswersRepairsCard = ({
  answers,
  card,
}: StructuredAnswersRepairsCardProps) => {
  if (!answers.topic_specific || !answers.topic_specific.REPAIRS) {
    return null
  }
  const repairs = answers.topic_specific.REPAIRS
  const data = [
    [
      { label: 'Problem start date', value: repairs.issue_start },
      {
        label: 'Problem description',
        value: repairs.issue_description?.label,
      },
      {
        label: 'Problem photo(s)',
        value: repairs.issue_photos?.map((file, index) => (
          <>
            {index > 0 && ' | '}
            <Anchor key={file.url} href={file.url} target="_blank">
              {file.name}
            </Anchor>
          </>
        )),
      },
      {
        label: 'Client actions taken',
        value: repairs.vcat?.map(({ label }) => label).join(' | '),
      },
      {
        label: 'Repairs required for',
        value: repairs.required?.join(' | '),
      },
    ],
  ]
  return (
    <StructuredAnswersCard
      title="Repairs information"
      data={data}
      card={card}
    />
  )
}
