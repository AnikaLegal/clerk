import React from 'react'
import styled from 'styled-components'

import { theme } from '../theme'

export const TextInput = ({ value, onChange, ...props }: any) => (
  <TextEl
    type="text"
    value={value || ''}
    onChange={(e) => onChange(e.target.value)}
    {...props}
  />
)

export const TextEl = styled.input`
  font-size: ${theme.text.subtitle};
  font-weight: 500;
  font-family: 'DM Sans', sans-serif;
  color: ${theme.color.teal.primary};
  width: 100%;
  height: 40px;
  display: block;
  box-sizing: border-box;
  outline: 0;
  border: 0;
  border-bottom: 2px solid ${theme.color.teal.quaternary};
  padding: 0;
  border-radius: 0;

  &::placeholder {
    color: ${theme.color.teal.quaternary};
  }
  &:focus {
    border-bottom: 2px solid ${theme.color.teal.primary};
  }
  &:disabled {
    background-color: transparent;
    cursor: not-allowed;
  }
`
