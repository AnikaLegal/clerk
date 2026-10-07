import React from 'react'
import styled from 'styled-components'
import { Button, Header } from 'semantic-ui-react'
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

export class ErrorBoundary extends React.Component<
  { noRender?: boolean; children?: React.ReactNode | undefined },
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
    const { noRender, children } = this.props
    if (hasError) {
      if (noRender) {
        return null
      }
      if (isServerDown) {
        return (
          <Error>
            <div>
              <Header>
                Anika Legal isn't responding right now
                <Header.Subheader>
                  This usually clears up within a few minutes, for example after
                  an update. Wait a moment, then reload the page. If it is still
                  not working after ten minutes, let us know in the{' '}
                  <strong>#tech</strong> channel.
                </Header.Subheader>
              </Header>
              <Button onClick={() => window.location.reload()}>Reload</Button>
            </div>
          </Error>
        )
      }
      return (
        <Error>
          <Header>
            Something broke, sorry!
            <Header.Subheader>
              Try refreshing the page. If it's still broken, let us know in the{' '}
              <strong>#tech</strong> channel, noting:
              <ul>
                <li>The page and URL you were visiting</li>
                <li>When the error occurred</li>
                <li>What you were trying to do</li>
                <li>What you expected to happen</li>
                <li>What actually happened</li>
              </ul>
            </Header.Subheader>
          </Header>
        </Error>
      )
    }
    return children
  }
}

const Error = styled.div`
  display: flex;
  flex-direction: column;
  width: 100%;
  justify-content: center;
  align-items: center;
  padding: 0 16px;
  box-sizing: border-box;

  .ui.header {
    max-width: 36rem;
  }
  .ui.header .sub.header {
    margin-top: 0.5em;
  }
  .ui.button {
    display: block;
    margin: 1em auto 0;
  }
`
