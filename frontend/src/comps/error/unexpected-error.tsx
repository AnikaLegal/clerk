import React from 'react'
import { List, Text } from '@mantine/core'
import { IconAlertTriangle } from '@tabler/icons-react'
import ErrorMessage, { ErrorScreenProps } from 'comps/error/error-message'

const UnexpectedError = ({ compact }: ErrorScreenProps) => (
  <ErrorMessage
    icon={
      <IconAlertTriangle
        size={64}
        stroke={1.75}
        color="var(--mantine-color-red-7)"
      />
    }
    title="Something broke, sorry!"
    compact={compact}
  >
    <Text>
      Try refreshing the page. If it's still broken, let us know in the{' '}
      <Text span fw={700}>
        #tech
      </Text>{' '}
      channel, noting:
    </Text>
    <List>
      <List.Item>The page and URL you were visiting</List.Item>
      <List.Item>When the error occurred</List.Item>
      <List.Item>What you were trying to do</List.Item>
      <List.Item>What you expected to happen</List.Item>
      <List.Item>What actually happened</List.Item>
    </List>
  </ErrorMessage>
)

export default UnexpectedError
