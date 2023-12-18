import React, { useEffect, useRef } from 'react'
import { hydrate, render } from 'react-dom'
import { Converter, setFlavor } from 'showdown'
import xss from 'xss'
import styled from 'styled-components'
import slackifyMarkdown from 'slackify-markdown'
import { Provider } from 'react-redux'
import { SnackbarProvider } from 'notistack'

import { ErrorBoundary } from 'comps/error-boundary'
import { store } from 'apiNew/store'
import { Error as ErrorType } from 'apiNew'

const converter = new Converter()
setFlavor('github')

export const MarkdownAsHtmlDisplay = ({ markdown, ...props }) => (
  <div
    dangerouslySetInnerHTML={{ __html: markdownToHtml(markdown) }}
    {...props}
  />
)

export const markdownToSlackyMarkdown = (markdownText) => {
  const slackyMarkdown = slackifyMarkdown(markdownText)
  // Sanitise HTML removing <script> tags and the like.
  // return xss(slackyMarkdown)
  return slackyMarkdown
}

export const markdownToHtml = (markdownText) => {
  const html = converter.makeHtml(markdownText)
  // Sanitise HTML removing <script> tags and the like.
  return xss(html)
}

// Skips first update
export const useEffectLazy = (func: () => void, vars: React.DependencyList) => {
  const isFirstUpdate = useRef(true)
  useEffect(() => {
    if (isFirstUpdate.current) {
      isFirstUpdate.current = false
    } else {
      func()
    }
  }, vars)
}

export const mount = (App: React.ComponentType) => {
  const root = document.getElementById('app')
  const rootComponent = (
    <Provider store={store}>
      <SnackbarProvider maxSnack={3}>
        <ErrorBoundary>
          <FadeInOnLoad>
            <App />
          </FadeInOnLoad>
        </ErrorBoundary>
      </SnackbarProvider>
    </Provider>
  )

  if (root.hasChildNodes()) {
    hydrate(rootComponent, root)
  } else {
    render(rootComponent, root)
  }
}

const FadeInOnLoad = styled.div`
  animation: fadein 0.3s;
  @keyframes fadein {
    from {
      opacity: 0;
    }
    to {
      opacity: 1;
    }
  }
`

export const debounce = (delay) => {
  let timer = null
  return (func) => {
    return (...args) => {
      clearTimeout(timer)
      timer = setTimeout(() => func(...args), delay)
    }
  }
}

// Debounce user input, returns a promise
export const debouncePromise = (delay) => {
  let timer = null
  return (func) => {
    return (...args) =>
      new Promise((resolve) => {
        clearTimeout(timer)
        timer = setTimeout(() => func(...args).then(resolve), delay)
      })
  }
}

// Wait n seconds
export const waitSeconds = (delay: number) =>
  new Promise((resolve) => setTimeout(() => resolve(null), delay * 1000))

export const useOutsideClick = (ref, onClickOutside) => {
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (ref.current && !ref.current.contains(event.target)) {
        onClickOutside()
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [ref])
}

export interface ErrorResult {
  data?: ErrorType
  status?: number
}

// Read API error message for display in a notification.
export const getAPIErrorMessage = (
  err: ErrorResult,
  baseMessage: string
): string => {
  if ('originalStatus' in err && err.originalStatus === 500) {
    return `${baseMessage}: something went very wrong`
  }

  if (!err.data) return baseMessage
  const formattedMessages = []
  for (let errorMessages of Object.values(err.data)) {
    if (Array.isArray(errorMessages)) {
      formattedMessages.push(errorMessages.join(', '))
    } else {
      formattedMessages.push(errorMessages)
    }
  }
  if (formattedMessages.length > 0) {
    return `${baseMessage}: ${formattedMessages.join(', ')}`
  } else {
    return baseMessage
  }
}

interface FormErrors {
  [key: string]: string
}

// Read API errors for display in a form.
export const getAPIFormErrors = (err: ErrorResult): FormErrors | null => {
  let statusNumber = null
  if (err && 'status' in err && typeof err.status === 'number') {
    statusNumber = err.status
  }
  let requestErrors: { [key: string]: string } | null = null
  if (statusNumber == 400 && 'data' in err) {
    requestErrors = Object.entries(err.data).reduce(
      (obj, [k, v]) => ({ ...obj, [k]: parseError(v) }),
      {}
    ) as { [key: string]: string }
  }
  return requestErrors
}

const parseError = (error: any) => {
  const isArray = Array.isArray(error)
  const isObject = typeof error === 'object'
  if (isArray) {
    return error.map((e) => String(e)).join(', ')
  } else if (isObject) {
    return Object.entries(error)
      .map(([k, v]) => `${k}: ${v}`)
      .join(', ')
  } else {
    return String(error)
  }
}
