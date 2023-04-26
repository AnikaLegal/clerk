import styled from 'styled-components'

import { theme } from './theme'

const Header = styled.h2`
  font-style: normal;
  font-weight: normal;
  font-size: 24px;
  line-height: 32px;
  color: ${theme.color.grey.dark};
  margin: 0 0 20px 0;
  @media (max-width: ${theme.screen.mobile}) {
    margin: 0 0 16px 0;
    ${theme.switch({
      splash: `
      font-weight: 500;
      font-size: 20px;
      line-height: 20px;
    `,
    })}
  }
  @media (max-width: ${theme.screen.small}) {
    margin: 0 0 13px 0;
    ${theme.switch({
      splash: `
      font-size: 16.74px;
      line-height: 16.74px;
    `,
    })}
  }
  &:last-child {
    margin: 0;
  }
  a {
    color: ${theme.color.teal.secondary};
    &::visited {
      color: ${theme.color.teal.secondary};
    }
  }
`

const Body = styled.p`
  font-style: normal;
  font-weight: normal;
  font-size: 20px;
  line-height: 28px;
  color: ${theme.color.grey.mid};
  margin: 0 0 15px 0;
  @media (max-width: ${theme.screen.mobile}) {
    margin: 0 0 12px 0;
    ${theme.switch({
      splash: `
        font-size: 16px;
        line-height: 16px;
    `,
    })}
  }
  @media (max-width: ${theme.screen.small}) {
    ${theme.switch({
      splash: `
        font-size: 13.4px;
        line-height: 14px;
    `,
    })}
  }
  &:last-child {
    margin: 0;
  }

  a {
    color: ${theme.color.teal.secondary};
    &::visited {
      color: ${theme.color.teal.secondary};
    }
  }
`

// Used for warning messages for stuff like Christmas closures.
const WarningBody = styled(Body)`
  background-color: ${theme.color.marigold};
  color: ${theme.color.grey.dark};
  font-size: 14px;
  line-height: 1.4;
  padding: 1rem;
  border-radius: 10px;
  & > strong {
    color: #d72207;
  }
`

export const Text = { Header, Body, WarningBody }
