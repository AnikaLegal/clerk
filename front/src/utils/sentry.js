// @flow
import * as Sentry from '@sentry/browser'

if (SENTRY_JS_DSN) {
  // Initialize Sentry, if it is enabled.
  Sentry.init({
    dsn: SENTRY_JS_DSN,
    environment: SENTRY_ENV,
  })
}

export const logError = (error: any) => {
  console.error('Caught an error:', error)
  const errorInfo = error.isAxiosError ? getAxiosErrorInfo(error) : {}
  if (errorInfo) {
    console.error('Error info:', errorInfo)
  }
  if (SENTRY_JS_DSN) {
    // Send error report to Sentry, if it is enabled.
    console.log('Sending error report to Sentry.')
    if (error.isAxiosError) {
      // Create a new error instance to try and fix the missing stack trace in Sentry.
      const url =
        error.config && error.config.url ? error.config.url : 'unknown URL'
      const msg = `${error.message} for ${url} `
      const e = new Error(msg)
      // Extract additional error data from Axios HTTP errors.
      Sentry.withScope((scope) => {
        scope.setExtras(errorInfo)
        Sentry.captureException(e)
      })
    } else {
      // Log all non-Axios errors with no additional data.
      Sentry.captureException(error)
    }
  }
}

// Extract extra data from failed Axios HTTP requests
const getAxiosErrorInfo = (e) => {
  let data, headers, responseData, responseHeaders
  try {
    data = JSON.stringify(e.config.data)
  } catch {
    data = ''
  }
  try {
    headers = JSON.stringify(e.config.headers)
  } catch {
    headers = ''
  }
  try {
    responseData = JSON.stringify(e.response.data)
  } catch {
    responseData = ''
  }
  try {
    responseHeaders = JSON.stringify(e.response.headers)
  } catch {
    responseHeaders = ''
  }
  const config: Object = e.config
    ? {
        url: e.config.url,
        method: e.config.method,
      }
    : {}
  const response = e.response
    ? {
        responseStatus: e.response.status,
        responseStatusText: e.response.statusText,
      }
    : {}
  return {
    ...config,
    requestData: data,
    requestHeaders: headers,
    responseMessage: e.message,
    ...response,
    responseHeaders: responseHeaders,
    responseData: responseData,
  }
}
