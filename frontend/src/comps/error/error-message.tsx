import React from 'react'
import { Center, Container, Stack, Text } from '@mantine/core'

export interface ErrorScreenProps {
  // For an error inside part of a page, where a full page height is too tall.
  compact?: boolean
}

interface ErrorMessageProps extends ErrorScreenProps {
  icon: React.ReactNode
  title: string
  children: React.ReactNode
}

const ErrorMessage = ({
  icon,
  title,
  compact,
  children,
}: ErrorMessageProps) => (
  <Container size="xl">
    <Center mih={compact ? undefined : '65vh'} py={compact ? 'xl' : undefined}>
      <Stack align="center" gap="xs" maw="36rem">
        {icon}
        <Text size="lg">{title}</Text>
        <Stack gap="xs" w="100%">
          {children}
        </Stack>
      </Stack>
    </Center>
  </Container>
)

export default ErrorMessage
