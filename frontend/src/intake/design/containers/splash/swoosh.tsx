import styled from 'styled-components'

import { theme } from '../../theme'

export const SplashSwoosh = styled.img`
    position: absolute;
    z-index: -1;
    top: 0;
    &.desktop {
      height: 100%;
      bottom: 0;
    }
    &.mobile {
      display: none;
    }
    &.mobile-small {
      display: none;
    }
    &.right {
      right: 0;
    }
    &.left {
      left: 0;
    }
  }
  @media (max-width: ${theme.screen.half}) {
    &.desktop {
      &.left {
        left: calc(-600px + 30vw);
      }
      &.right {
        right: calc(-600px + 30vw);
      }
    }
  }
  @media (max-width: ${theme.screen.mobile}) {
    &.mobile {
      display: block;
    }
    &.desktop {
      display: none;
    }
  }
  @media (max-width: ${theme.screen.small}) {
    &.mobile {
      display: none;
    }
    &.mobile-small {
      display: block;
    }
  }
`
