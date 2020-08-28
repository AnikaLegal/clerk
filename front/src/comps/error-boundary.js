// @flow
import React, { Component } from 'react'
import PropTypes from 'prop-types'
import styled from 'styled-components'
import type { Node } from 'react'

import { logError } from 'utils'

type Props = {
  children: Node,
  noRender?: boolean,
}

type State = {
  hasError: boolean,
}

export class ErrorBoundary extends Component<Props, State> {
  static propTypes = {
    children: PropTypes.node.isRequired,
    noRender: PropTypes.bool,
  }

  state = { hasError: false }

  componentDidCatch = (error: any) => {
    this.setState({ hasError: true })
    logError(error)
  }

  render() {
    const { hasError } = this.state
    const { noRender, children } = this.props
    if (hasError) {
      if (noRender) {
        return null
      }
      return (
        <Error>
          <h2>Something broke 😠</h2>
        </Error>
      )
    }
    return children
  }
}

const Error = styled.div`
  display: flex;
  width: 100%;
  height: 100%;
  justify-content: center;
  align-items: center;
`
