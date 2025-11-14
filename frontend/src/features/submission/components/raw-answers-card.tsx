import { Card, CardProps, Code } from '@mantine/core'
import React from 'react'

export interface SubmissionRawAnswersCardProps {
  data: object
  card?: CardProps
}

export const SubmissionRawAnswersCard = ({
  data,
  card,
}: SubmissionRawAnswersCardProps) => {
  return (
    <Card {...card}>
      <Card.Section>
        <Code block bg="var(--mantine-color-default)">
          {JSON.stringify(data, null, 2)}
        </Code>
      </Card.Section>
    </Card>
  )
}
