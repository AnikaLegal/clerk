// @flow
import React from 'react'
import styled from 'styled-components'

import { theme } from '../theme'

const SwooshContainer = styled.div`
  position: relative;
  height: ${({ height }) => height}px;
  width: 100%;
  z-index: -1;
  svg {
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
  }
`

type Props = {
  height: number,
}

export const LeftSwoosh = ({ height }: Props) => (
  <SwooshContainer height={height}>
    <svg
      width={(height * 998) / 900}
      height={height}
      viewBox="0 0 998 900"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        d="M-160.268 -2.24508C-81.8371 -28.6936 998 -2.24508 998 -2.24508C998 -2.24508 934.506 52.3651 800.406 194.151C666.306 335.937 713.545 485.739 543.364 702.176C373.183 918.612 315.309 899.574 315.309 899.574H-306.393C-306.393 899.574 -420.259 377.024 -306.393 159.939C-306.393 159.939 -238.698 24.2035 -160.268 -2.24508Z"
        fill="#FFE1A6"
      />
    </svg>
  </SwooshContainer>
)

export const RightSwoosh = ({ height }: Props) => (
  <SwooshContainer height={height}>
    <svg
      width={(height * 830) / 900}
      height={height}
      viewBox="0 0 830 900"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        d="M829.575 0.5H0C0 0.5 45.1985 51.4382 140.5 193.5C235.802 335.562 202.229 485.655 323.173 702.513C444.116 919.37 485.246 900.295 485.246 900.295H829.575V0.5Z"
        fill="#FFE1A6"
      />
    </svg>
  </SwooshContainer>
)
