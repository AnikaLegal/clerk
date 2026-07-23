import { Component, ReactNode } from 'react'

import { LINKS } from '../consts'
import { logException } from '../utils'

interface Props {
  children: ReactNode
}

interface State {
  hasError: boolean
}

export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false }

  static getDerivedStateFromError(): State {
    return { hasError: true }
  }

  componentDidCatch(error: unknown) {
    logException(error)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="intake-splash">
          <h1>Something went wrong</h1>
          <p>
            Sorry, something broke. Please refresh the page to continue - your
            answers are saved on this device. If the problem persists, please{' '}
            <a href={LINKS.CONTACT}>contact us</a>.
          </p>
        </div>
      )
    }
    return this.props.children
  }
}
