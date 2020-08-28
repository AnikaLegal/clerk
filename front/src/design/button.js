// @flow
import React from 'react'
import styled from 'styled-components'

import { theme } from './theme'

export const BigButton = styled.button`
  height: 48px;
  font-size: ${theme.text.title};
  line-height: 32px;
  font-weight: 700;
  border-radius: 20px;
  outline: none;

  /* Default is secondary button */
  padding: 6px 38px 10px 38px;
  color: ${theme.color.tealLight};
  background-color: ${theme.color.white};
  border: 2px solid ${theme.color.tealLight};
  box-sizing: border-box;
  &:hover {
    box-shadow: ${theme.shadow};
  }
  ${theme.switch({
    primary: `
      color: ${theme.color.white};
      border: none;
      background-color: ${theme.color.teal};
      padding: 8px 40px;
      &:active {
        outline: none;
        box-shadow: 0 0 0 1px ${theme.color.teal};
        border: solid 1px ${theme.color.white};
        padding: 7px 39px;

      }
      `,
  })}
  &:focus {
    outline: none;
  }
  &:disabled {
    opacity: 0.2;
  }
  & + & {
    margin-left: 30px;
  }
  @media (max-width: ${theme.screen.mobile}) {
    width: 100%;
    & + & {
      margin-left: 0px;
      margin-top: 16px;
    }
  }
`

const _Button = styled.button`
  color: ${theme.color.white};
  font-weight: 700;
  border-radius: 20px;
  border: none;
  /* Default is secondary button */
  background-color: ${theme.color.tealLight};

  ${theme.switch({
    primary: `
      background-color: ${theme.color.teal};
      `,
  })}

  &:hover {
    background-color: ${theme.color.teal};
  }
  &:focus {
    outline: none;
  }
  &:active {
    outline: none;
    box-shadow: 0 0 0 1px ${theme.color.teal};
    border: solid 1px ${theme.color.white};
  }
  &:disabled {
    opacity: 0.2;
  }
  & + & {
    margin-left: 10px;
  }

  padding: 8px 20px;
  font-size: ${theme.text.subtitle};
  line-height: 28px;
  &:active {
    padding: 7px 19px;
  }
  @media (max-width: ${theme.screen.mobile}) {
    width: 100%;
    & + & {
      margin-left: 0px;
      margin-top: 16px;
    }
  }
`

const _IconWrapper = styled.span`
  margin-left: 10px;
`

export const Button = ({ children, Icon, ...props }: any) => (
  <_Button {...props}>
    {children}
    {Icon && (
      <_IconWrapper>
        <Icon />
      </_IconWrapper>
    )}
  </_Button>
)
