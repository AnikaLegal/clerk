import styled from 'styled-components'

import { theme } from '../theme'

export const AppContainer = styled.div`
  padding: 0;
  box-sizing: border-box;
  min-height: 100%;

  @media (max-width: ${theme.screen.mobile}) {
    padding: 0 16px 0 16px;
  }
`
