import { Anchor, CardProps } from '@mantine/core'
import { SubmissionAnswers } from 'api'
import React from 'react'
import { StructuredAnswersCard } from '../structured-answers-card'

export interface StructuredAnswersBondsCardProps {
  answers: SubmissionAnswers
  card?: CardProps
}

export const StructuredAnswersBondsCard = ({
  answers,
  card,
}: StructuredAnswersBondsCardProps) => {
  if (!answers.topic_specific || !answers.topic_specific.BONDS) {
    return null
  }
  const bonds = answers.topic_specific.BONDS
  const data = [
    [
      { label: 'Move out date', value: bonds.move_out_date },
      {
        label: 'RP intends to make claim?',
        value: bonds.landlord_intents_to_make_claim?.label,
      },
      {
        label: 'Tenant has RTBA application copy?',
        value: bonds.tenant_has_rtba_application_copy?.label,
      },
      {
        label: 'RTBA application',
        value: bonds.rtba_application?.map((file, index) => (
          <>
            {index > 0 && ' | '}
            <Anchor key={file.url} href={file.url} target="_blank">
              {file.name}
            </Anchor>
          </>
        )),
      },
      {
        label: 'Claim reason(s)',
        value: bonds.claim_reasons?.slice().sort().join(' | '),
      },
    ],
    [
      {
        label: 'Cleaning claim description',
        value: bonds.cleaning_claim_description,
      },
      {
        label: 'Cleaning claim amount',
        value: bonds.cleaning_claim_amount,
      },
      {
        label: 'Cleaning-related documents',
        value: bonds.cleaning_documents?.map((file, index) => (
          <>
            {index > 0 && ' | '}
            <Anchor key={file.url} href={file.url} target="_blank">
              {file.name}
            </Anchor>
          </>
        )),
      },
    ],
    [
      {
        label: 'Damage claim description',
        value: bonds.damage_claim_description,
      },
      {
        label: 'Damage claim amount',
        value: bonds.damage_claim_amount,
      },
      {
        label: 'Damage caused by tenant?',
        value: bonds.damage_caused_by_tenant?.label,
      },
      {
        label: 'Tenants quote for damage repairs',
        value: bonds.damage_quote?.map((file, index) => (
          <>
            {index > 0 && ' | '}
            <Anchor key={file.url} href={file.url} target="_blank">
              {file.name}
            </Anchor>
          </>
        )),
      },
    ],
    [
      {
        label: 'Locks claim amount',
        value: bonds.locks_claim_amount,
      },
      {
        label: 'Locks changed by tenant?',
        value: bonds.locks_changed_by_tenant?.label,
      },
      {
        label: 'Tenants quote for lock changes',
        value: bonds.locks_change_quote?.map((file, index) => (
          <>
            {index > 0 && ' | '}
            <Anchor key={file.url} href={file.url} target="_blank">
              {file.name}
            </Anchor>
          </>
        )),
      },
    ],
    [
      {
        label: 'Money owed claim description',
        value: bonds.money_owed_claim_description,
      },
      {
        label: 'Money owed claim amount',
        value: bonds.money_owed_claim_amount,
      },
      {
        label: 'Money owed by tenant?',
        value: bonds.money_is_owed_by_tenant?.label,
      },
    ],
    [
      {
        label: 'Other claim description',
        value: bonds.other_reasons_description,
      },
      {
        label: 'Other claim amount',
        value: bonds.other_reasons_amount,
      },
    ],
  ]
  return (
    <StructuredAnswersCard title="Bond information" data={data} card={card} />
  )
}
