import React from 'react'
import styled from 'styled-components'

import { theme } from '../theme'

export const TextInputOptions = ({ value, onChange, ...props }: any) => (
  <TextInputOptionsEl
    type="text"
    onChange={(e) => onChange(e.target.value)}
    {...props}
  />
)

export const TextInputOptionsEl = styled.input`
  font-family: 'DM Sans', sans-serif;
  width: 100%;
  max-width: 380px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: ${theme.text.subtitle};
  font-weight: 500;
  line-height: 28px;
  color: ${theme.color.teal.primary};
  box-sizing: border-box;
  outline: 0;
  border: 0;
  padding: 8px 20px;
  margin-top: 5px;
  border-bottom: 2px solid ${theme.color.teal.quaternary};
  &:focus {
    border-bottom: 2px solid ${theme.color.teal.primary};
  }
  &::placeholder {
    color: ${theme.color.teal.quaternary};
  }
  &:disabled {
    background-color: transparent;
    cursor: not-allowed;
  }
  @media (max-width: ${theme.screen.mobile}) {
    font-size: 16px;
  }
  @media (max-width: ${theme.screen.small}) {
    font-size: 13.4px;
  }
`
