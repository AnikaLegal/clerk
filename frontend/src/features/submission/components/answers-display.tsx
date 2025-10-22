import { Box, Center } from '@mantine/core'
import api from 'api'
import React from 'react'
import { SubmissionRawAnswersCard } from './raw-answers-card'
import { EmptyState, LoadingState } from './answers-display-states'
import { SubmissionStructuredAnswers } from './structured-answers'

export interface SubmissionAnswersDisplayProps {
  submissionId: string
  showRawAnswers: boolean
}

export const SubmissionAnswersDisplay = ({
  submissionId,
  showRawAnswers,
}: SubmissionAnswersDisplayProps) => {
  const result = api.useGetSubmissionQuery({ id: submissionId })

  if (result.isFetching) {
    return (
      <Center>
        <LoadingState />
      </Center>
    )
  }
  if (!result.data) {
    return (
      <Center>
        <EmptyState />
      </Center>
    )
  }
  return (
    <Box mt="sm">
      {showRawAnswers ? (
        <SubmissionRawAnswersCard
          data={result.data.answers_raw}
          card={{ withBorder: true }}
        />
      ) : (
        <SubmissionStructuredAnswers data={result.data.answers} />
      )}
    </Box>
  )
}
