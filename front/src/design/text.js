// @flow
import React from 'react'
import styled from 'styled-components'

import { theme } from './theme'

const Header = styled.h2`
  font-style: normal;
  font-weight: normal;
  font-size: ${theme.text.title};
  line-height: 32px;
  color: ${theme.color.grey.dark};
  margin: 0 0 20px 0;
`

const Body = styled.p`
  font-style: normal;
  font-weight: normal;
  font-size: ${theme.text.subtitle};
  line-height: 28px;
  color: ${theme.color.grey.mid};
  margin: 0 0 20px 0;
`

export const Text = { Header, Body }
