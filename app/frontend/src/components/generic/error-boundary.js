import React, { Component } from 'react'
import styles from 'styles/generic/error-boundary.module.scss'

export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false }
  }

  componentDidCatch(error, info) {
    console.error(error, info) // eslint-disable-line no-console
    this.setState({ hasError: true })
  }

  render() {
    const { hasError } = this.state
    const { noRender, children } = this.props
    if (hasError) {
      if (noRender) {
        return null
      }
      return (
        <div className={styles.error}>
          <h2>Something broke 😠</h2>
        </div>
      )
    }
    return children
  }
}
