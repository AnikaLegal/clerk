import * as Sentry from '@sentry/browser'

interface SentryContext {
  dsn: string
  environment: string
}

export const initSentry = () => {
  const context = (window as { SENTRY_CONTEXT?: SentryContext }).SENTRY_CONTEXT
  if (context?.dsn) {
    Sentry.init({ dsn: context.dsn, environment: context.environment })
  }
}

export const logException = (error: unknown) => {
  console.error(error)
  Sentry.captureException(error)
}
