import { Anchor, CardProps } from '@mantine/core'
import { SubmissionAnswers } from 'api'
import React from 'react'
import { StructuredAnswersCard } from '../structured-answers-card'

export interface StructuredAnswersEvictionArrearsCardProps {
  answers: SubmissionAnswers
  card?: CardProps
}

export const StructuredAnswersEvictionArrearsCard = ({
  answers,
  card,
}: StructuredAnswersEvictionArrearsCardProps) => {
  if (!answers.topic_specific || !answers.topic_specific.EVICTION_ARREARS) {
    return null
  }
  const evictions = answers.topic_specific.EVICTION_ARREARS
  const data = [
    [
      { label: 'Has VCAT hearing date?', value: evictions.is_vcat_date?.label },
      { label: 'VCAT hearing date', value: evictions.vcat_date },
      { label: 'NTV vacate date', value: evictions.notice_vacate_date },
      { label: 'NTV send date', value: evictions.notice_send_date },
      {
        label: 'NTV received date',
        value: evictions.doc_delivery_time_notice_to_vacate,
      },
      {
        label: 'Reason for arrears',
        value: evictions.payment_fail_reason?.join(' | '),
      },
      {
        label: 'Arrears reason description',
        value: evictions.payment_fail_description,
      },
    ],
    [
      {
        label: 'Documents provided',
        value: evictions.documents_provided?.join(' | '),
      },
      {
        label: 'Documents',
        value: evictions.documents?.map((file, index) => (
          <>
            {index > 0 && ' | '}
            <Anchor key={file.url} href={file.url} target="_blank">
              {file.name}
            </Anchor>
          </>
        )),
      },
      {
        label: 'NTV delivery method',
        value: evictions.delivery_method_notice_to_vacate,
      },
      {
        label: 'Possession order delivery method',
        value: evictions.delivery_method_possession_order,
      },
      {
        label: 'Other documents delivery method',
        value: evictions.delivery_method_other_docs,
      },
      {
        label: 'Possession order date received',
        value: evictions.doc_delivery_time_possession_order,
      },
      {
        label: 'Other documents date received',
        value: evictions.doc_delivery_time_other_docs,
      },
    ],
    [
      {
        label: 'Rent in arrears',
        value: evictions.rent_unpaid,
      },
      {
        label: 'Rent cycle',
        value: evictions.rent_cycle,
      },
      {
        label: 'Is on payment plan?',
        value: evictions.is_on_payment_plan?.label,
      },
      {
        label: 'Could afford payment plan?',
        value: evictions.can_afford_payment_plan?.label,
      },
      {
        label: 'Possible payment plan amount',
        value: evictions.payment_amount,
      },
      {
        label: 'Circumstance change affecting payment',
        value: evictions.payment_fail_change,
      },
      {
        label: 'Miscellaneous comments',
        value: evictions.miscellaneous,
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
