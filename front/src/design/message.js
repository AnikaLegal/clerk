// @flow
import * as React from 'react'
import styled from 'styled-components'

import { Icon } from './shapes'
import { theme } from './theme'

type Props = {
  children: React.Node,
}

const ErrorEl = styled.div`
  display: flex;
  align-items: center;
  color: ${theme.color.error.primary};
  background-color: ${theme.color.error.secondary};
  padding: 3px 10px;
  font-size: ${theme.text.subtitle};
  & + & {
    margin-top: 5px;
  }
`

export const ErrorMessage = ({ children }: Props) => (
  <ErrorEl>
    <Icon.Error style={{ marginRight: '5px' }} />
    {children}
  </ErrorEl>
)
