import React from 'react'
import { Button, Center, Container, List, Stack, Text } from '@mantine/core'
import { IconAlertTriangle, IconCloudOff } from '@tabler/icons-react'
import * as Sentry from '@sentry/browser'
import {
  ApiRequestError,
  isServerError,
  toReportableError,
} from 'comps/error/api-error'

interface SentryContext {
  dsn: string
  environment: string
}
const SENTRY_CONTEXT = (window as any).SENTRY_CONTEXT as SentryContext
if (SENTRY_CONTEXT.dsn) {
  // Initialize Sentry, if it is enabled.
  Sentry.init({
    dsn: SENTRY_CONTEXT.dsn,
    environment: SENTRY_CONTEXT.environment,
  })
}

export const logException = (error) => {
  console.error('Caught an error:', error)
  if (SENTRY_CONTEXT.dsn) {
    // Send error report to Sentry, if it is enabled.
    console.log('Sending error report to Sentry.')
    const reportable = toReportableError(error)
    Sentry.captureException(
      reportable,
      // These errors share this boundary's stack, so group them by message.
      reportable instanceof ApiRequestError
        ? { fingerprint: [reportable.message] }
        : undefined
    )
  } else {
    console.log('Sentry not enabled.')
  }
}

const ErrorMessage = ({
  icon,
  title,
  compact,
  children,
}: {
  icon: React.ReactNode
  title: string
  compact?: boolean
  children: React.ReactNode
}) => (
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

export class ErrorBoundary extends React.Component<
  {
    noRender?: boolean
    // For a boundary around part of a page, where a full page height is too tall.
    compact?: boolean
    children?: React.ReactNode | undefined
  },
  { hasError: boolean; isServerDown: boolean }
> {
  constructor(props) {
    super(props)
    this.state = { hasError: false, isServerDown: false }
  }

  componentDidCatch(error) {
    const isServerDown = isServerError(error)
    this.setState({ hasError: true, isServerDown })
    // The backend reports its own errors, and an outage is for uptime
    // monitoring to catch, so a server error is not reported from here.
    if (!isServerDown) {
      logException(error)
    }
  }

  render() {
    const { hasError, isServerDown } = this.state
    const { noRender, compact, children } = this.props
    if (hasError) {
      if (noRender) {
        return null
      }
      if (isServerDown) {
        return (
          <ErrorMessage
            icon={
              <IconCloudOff
                size={64}
                stroke={1.75}
                color="var(--mantine-color-dark-4)"
              />
            }
            title="Clerk is temporarily unavailable"
            compact={compact}
          >
            <Text>
              This usually clears up within a few minutes. Reload the page in a
              moment. If it's still down after ten minutes, let us know in{' '}
              <Text span fw={700}>
                #tech
              </Text>
              .
            </Text>
            <Center>
              <Button onClick={() => window.location.reload()}>Reload</Button>
            </Center>
          </ErrorMessage>
        )
      }
      return (
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
    }
    return children
  }
}
