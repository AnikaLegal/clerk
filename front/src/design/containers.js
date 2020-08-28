// @flow
import * as React from 'react'
import styled from 'styled-components'

import { theme } from './theme'

export const HeroContainer = styled.div``

export const TextContainerOuter = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
`

export const TextContainerInner = styled.div`
  max-width: 700px;
  padding-left: 16px;
  padding-right: 16px;
`

type Props = {
  children: React.Node,
}

export const TextContainer = ({ children }: Props) => (
  <TextContainerOuter>
    <TextContainerInner>{children}</TextContainerInner>
  </TextContainerOuter>
)
