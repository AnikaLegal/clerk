import React from "react";
import styled from "styled-components";
import { Header } from "semantic-ui-react";
import * as Sentry from "@sentry/browser";

const SENTRY_JS_DSN = window && window.SENTRY_JS_DSN;

if (SENTRY_JS_DSN) {
  // Initialize Sentry, if it is enabled.
  Sentry.init({ dsn: SENTRY_JS_DSN });
}

export const logException = (error) => {
  console.error("Caught an error:", error);
  if (SENTRY_JS_DSN) {
    // Send error report to Sentry, if it is enabled.
    console.log("Sending error report to Sentry.");
    Sentry.captureException(error);
  } else {
    console.log("Sentry not enabled.");
  }
};

export class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  componentDidCatch(error) {
    this.setState({ hasError: true });
    logException(error);
  }

  render() {
    const { hasError } = this.state;
    const { noRender, children } = this.props;
    if (hasError) {
      if (noRender) {
        return null;
      }
      return (
        <Error>
          <Header>
            Something broke, sorry!
            <Header.Subheader>
              Try refreshing the page. If it's still broken, let us know in the{" "}
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
      );
    }
    return children;
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
`;
