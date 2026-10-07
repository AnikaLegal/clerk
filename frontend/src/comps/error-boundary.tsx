import React from 'react'
import * as Sentry from '@sentry/browser'
import {
  ApiRequestError,
  isServerError,
  toReportableError,
} from 'comps/error/api-error'
import ServerError from 'comps/error/server-error'
import UnexpectedError from 'comps/error/unexpected-error'

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

interface ErrorBoundaryProps {
  noRender?: boolean
  // Sized for a boundary around part of a page, not the full page height.
  compact?: boolean
  children?: React.ReactNode | undefined
}

interface ErrorBoundaryState {
  hasError: boolean
  error: unknown
}

export class ErrorBoundary extends React.Component<
  ErrorBoundaryProps,
  ErrorBoundaryState
> {
  state: ErrorBoundaryState = { hasError: false, error: undefined }

  // Anything can be thrown, including undefined, so the flag is kept apart.
  static getDerivedStateFromError(error: unknown) {
    return { hasError: true, error }
  }

  componentDidCatch(error: unknown) {
    // The backend reports its own errors, and an outage is for uptime
    // monitoring to catch, so a server error is not reported from here.
    if (!isServerError(error)) {
      logException(error)
    }
  }

  render() {
    const { hasError, error } = this.state
    const { noRender, compact, children } = this.props
    if (!hasError) {
      return children
    }
    if (noRender) {
      return null
    }
    return isServerError(error) ? (
      <ServerError compact={compact} />
    ) : (
      <UnexpectedError compact={compact} />
    )
  }
}
