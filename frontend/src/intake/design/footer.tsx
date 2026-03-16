import styled from 'styled-components'

import { theme } from './theme'

export const FadeFooter = styled.div`
  position: sticky;
  bottom: 0;
  left: 0;
  right: 0;
  height: 0;
  pointer-events: none;
  @media (max-width: ${theme.screen.mobile}) {
    height: 76px;
  }
  @media (max-width: ${theme.screen.small}) {
    height: 40px;
  }
  background: linear-gradient(
    360deg,
    #ffffff 21.06%,
    rgba(255, 255, 255, 0) 94.14%
  );
`
