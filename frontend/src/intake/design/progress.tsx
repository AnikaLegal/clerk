import React from 'react'
import styled from 'styled-components'

import { theme } from './theme'

interface Props {
  current: number
  steps: string[]
}
export const StepProgress: React.FC<Props> = ({ current, steps }) => {
  const length = steps.length
  return (
    <StepProgressEl>
      {steps.map((label, idx) => {
        const isCurrent = idx === current
        const hasNext = idx < length - 1
        return (
          <React.Fragment key={label}>
            <StepOuterEl active={isCurrent}>
              <StepInnerEl />
              {isCurrent && <StepLabelEl>{label}</StepLabelEl>}
            </StepOuterEl>
            {hasNext && <StepBarEl />}
          </React.Fragment>
        )
      })}
    </StepProgressEl>
  )
}

const StepProgressEl = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 34px 0;
  @media (max-width: ${theme.screen.mobile}) {
    display: none;
  }
`
const StepOuterEl = styled.div`
  border: 3px solid transparent;
  width: 39px;
  height: 39px;
  border-radius: 39px;
  box-sizing: border-box;
  display: flex;
  justify-content: center;
  align-items: center;
  ${theme.switch({
    active: `border: 3px solid ${theme.color.teal.tertiary};`,
  })}
  position: relative;
`
const StepLabelEl = styled.div`
  position: absolute;
  width: 120px;
  text-align: center;
  bottom: -34px;
  font-weight: 500;
  font-size: 16px;
  line-height: 24px;
  color: ${theme.color.teal.secondary};
`
const StepInnerEl = styled.div`
  width: 7px;
  height: 7px;
  border-radius: 7px;
  background-color: ${theme.color.teal.primary};
`
const StepBarEl = styled.div`
  border-top: 2px solid ${theme.color.grey.light};
  width: 95px;
  height: 1px;
  margin: 0 4px;
`
