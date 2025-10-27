import { Box, Group, Text } from '@mantine/core'
import { IconExclamationCircle } from '@tabler/icons-react'
import { SubmissionAnswers } from 'api'
import React from 'react'
import {
  StructuredAnswersAgentCard,
  StructuredAnswersBondsCard,
  StructuredAnswersClientCard,
  StructuredAnswersEvictionArrearsCard,
  StructuredAnswersEvictionRetaliatoryCard,
  StructuredAnswersHealthCheckCard,
  StructuredAnswersLandlordCard,
  StructuredAnswersOtherCaseCard,
  StructuredAnswersOtherInformationCard,
  StructuredAnswersRentReductionCard,
  StructuredAnswersRepairsCard,
  StructuredAnswersSupportWorkerCard,
  StructuredAnswersTenancyCard,
} from './structured-answers-cards'

export interface SubmissionStructuredAnswersProps {
  data: SubmissionAnswers | null
}

export const SubmissionStructuredAnswers = ({
  data,
}: SubmissionStructuredAnswersProps) => {
  return (
    <Box>
      {data ? (
        <>
          <StructuredAnswersClientCard
            answers={data}
            card={{ mt: 'md', withBorder: true }}
          />
          <StructuredAnswersSupportWorkerCard
            answers={data}
            card={{ mt: 'md', withBorder: true }}
          />
          <StructuredAnswersTenancyCard
            answers={data}
            card={{ mt: 'md', withBorder: true }}
          />
          <StructuredAnswersAgentCard
            answers={data}
            card={{ mt: 'md', withBorder: true }}
          />
          <StructuredAnswersLandlordCard
            answers={data}
            card={{ mt: 'md', withBorder: true }}
          />
          <StructuredAnswersOtherInformationCard
            answers={data}
            card={{ mt: 'md', withBorder: true }}
          />
          <StructuredAnswersRepairsCard
            answers={data}
            card={{ mt: 'md', withBorder: true }}
          />
          <StructuredAnswersBondsCard
            answers={data}
            card={{ mt: 'md', withBorder: true }}
          />
          <StructuredAnswersEvictionArrearsCard
            answers={data}
            card={{ mt: 'md', withBorder: true }}
          />
          <StructuredAnswersEvictionRetaliatoryCard
            answers={data}
            card={{ mt: 'md', withBorder: true }}
          />
          <StructuredAnswersHealthCheckCard
            answers={data}
            card={{ mt: 'md', withBorder: true }}
          />
          <StructuredAnswersRentReductionCard
            answers={data}
            card={{ mt: 'md', withBorder: true }}
          />
          <StructuredAnswersOtherCaseCard
            answers={data}
            card={{ mt: 'md', withBorder: true }}
          />
        </>
      ) : (
        <Group justify="center" gap="xs" m="sm">
          <IconExclamationCircle />
          <Text>Could not structure submission data</Text>
        </Group>
      )}
    </Box>
  )
}
