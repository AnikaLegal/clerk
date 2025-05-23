import { createTheme, MantineProvider } from '@mantine/core'
import { ModalsProvider } from '@mantine/modals'
import { Error as ErrorType } from 'api'
import { store } from 'api/store'
import { ErrorBoundary } from 'comps/error-boundary'
import { SnackbarProvider } from 'notistack'
import React, { useEffect, useRef } from 'react'
import { createRoot } from 'react-dom/client'
import { Provider } from 'react-redux'
import { Converter, setFlavor } from 'showdown'
import slackifyMarkdown from 'slackify-markdown'
import styled from 'styled-components'
import xss, { OnTagAttrHandler } from 'xss'

const theme = createTheme({
  fontFamily: "Lato,'Helvetica Neue',Arial,Helvetica,sans-serif",
})

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

/* It is safe to allow the HTML class attribute. See
 * https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html#safe-sinks
 * We allow this for styling.
 */
const ignoreTagAttrHandler: OnTagAttrHandler = (
  tag,
  name,
  value,
  isWhiteAttr
) => {
  if (name == 'class') {
    return `${name}="${value}"`
  }
}

export const markdownToHtml = (markdownText) => {
  const html = converter.makeHtml(markdownText)
  // Sanitise HTML removing <script> tags and the like.
  return xss(html, { onIgnoreTagAttr: ignoreTagAttrHandler })
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
  const domNode = document.getElementById('app')
  const reactNode = (
    <Provider store={store}>
      <SnackbarProvider maxSnack={3}>
        <MantineProvider theme={theme}>
          <ModalsProvider>
            <ErrorBoundary>
              <FadeInOnLoad>
                <App />
              </FadeInOnLoad>
            </ErrorBoundary>
          </ModalsProvider>
        </MantineProvider>
      </SnackbarProvider>
    </Provider>
  )

  if (!domNode.hasChildNodes()) {
    const root = createRoot(domNode)
    root.render(reactNode)
  }
  /*
  else {
    // TODO: hydration?
  }
  */
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

export const choiceToMap = (choices: string[][]): Map<string, string> => {
  return choices.reduce((map, entry) => {
    map.set(entry[0], entry[1])
    return map
  }, new Map())
}

interface OptionItem {
  key: string
  text: string
  value: string
}

export const choiceToOptions = (choices: string[][]): Array<OptionItem> =>
  choices.map(([value, label]) => ({
    key: label,
    text: label,
    value: value,
  }))

/* A helper function to remove "empty" attributes from an object preserving type info.
 */
type Entry<T> = { [K in keyof T]: [K, T[K]] }[keyof T]

export const filterEmpty = <T extends {}, V = Entry<T>>(obj: T): V =>
  filterObject(
    obj,
    ([, v]) =>
      !(
        (typeof v === 'string' && !v.length) ||
        v === null ||
        typeof v === 'undefined'
      )
  )

export const filterObject = <T extends {}, V = Entry<T>>(
  obj: T,
  fn: (entry: Entry<T>, i: number, arr: Entry<T>[]) => boolean
): V => Object.fromEntries((Object.entries(obj) as Entry<T>[]).filter(fn)) as V
