import { Anchor, CardProps } from '@mantine/core'
import { SubmissionAnswers } from 'api'
import React from 'react'
import { StructuredAnswersCard } from '../structured-answers-card'

export interface StructuredAnswersEvictionRetaliatoryCardProps {
  answers: SubmissionAnswers
  card?: CardProps
}

export const StructuredAnswersEvictionRetaliatoryCard = ({
  answers,
  card,
}: StructuredAnswersEvictionRetaliatoryCardProps) => {
  if (!answers.topic_specific || !answers.topic_specific.EVICTION_RETALIATORY) {
    return null
  }
  const eviction = answers.topic_specific.EVICTION_RETALIATORY
  const data = [
    [
      { label: 'NTV received', value: eviction.date_received_ntv },
      { label: 'Has NTV?', value: eviction.has_notice?.label },
      {
        label: 'Is tenant already removed?',
        value: eviction.is_already_removed?.label,
      },
      { label: 'NTV type', value: eviction.ntv_type },
      {
        label: 'Retaliatory reason',
        value: eviction.retaliatory_reason?.join(' | '),
      },
      {
        label: 'Retaliatory reason other',
        value: eviction.retaliatory_reason_other,
      },
      { label: 'Termination date', value: eviction.termination_date },
      { label: 'Has VCAT hearing?', value: eviction.vcat_hearing?.label },
      { label: 'VCAT hearing date', value: eviction.vcat_hearing_date },
      {
        label: 'Documents',
        value: eviction.documents?.map((file, index) => (
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
      title="Eviction information"
      data={data}
      card={card}
    />
  )
}
