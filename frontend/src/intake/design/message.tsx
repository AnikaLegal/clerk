import * as React from 'react'
import styled from 'styled-components'

import { Icon } from './icons'
import { theme } from './theme'

type Props = {
  children: React.ReactChildren | string
}

const ErrorEl = styled.div`
  display: flex;
  align-items: center;
  color: ${theme.color.error.primary};
  background-color: ${theme.color.error.secondary};
  padding: 3px 10px;
  font-size: ${theme.text.subtitle};
  margin-top: 8px;
  @media (max-width: ${theme.screen.mobile}) {
    font-size: 12px;
    padding: 5px 10px;
  }
`

export const ErrorMessage = ({ children }: Props) => (
  <ErrorEl>
    <Icon.Error style={{ marginRight: '5px' }} />
    {children}
  </ErrorEl>
)
