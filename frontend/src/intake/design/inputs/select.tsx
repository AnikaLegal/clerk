import React from 'react'
import styled from 'styled-components'

import { theme } from '../theme'
import { Icon } from '../icons'

type Option = { label: string; value: any }

type Props = {
  value: any
  onChange: (any) => void
  options: Array<Option>
}

export const SelectInput = ({ value, onChange, options }: Props) => {
  return (
    <SelectEl>
      {options.map((option) => (
        <SelectButtonEl
          key={option.label}
          selected={value === option.value}
          onClick={() => onChange(option.value)}
        >
          {option.label}{' '}
          {value === option.value && (
            <Icon.Tick color={theme.color.teal.primary} />
          )}
        </SelectButtonEl>
      ))}
    </SelectEl>
  )
}

const SelectButtonEl = styled.div`
  display: flex;
  cursor: pointer;
  align-items: center;
  justify-content: space-between;
  font-size: ${theme.text.subtitle};
  font-weight: 500;
  line-height: 28px;
  color: ${theme.color.teal.secondary};
  border: 1px solid ${theme.color.teal.tertiary};
  background-color: ${theme.color.teal.quinary};
  box-sizing: border-box;
  border-radius: 20px;
  padding: 8px 20px;
  & + & {
    margin-top: 8px;
  }
  &:hover {
    box-shadow: ${theme.shadow};
    color: ${theme.color.teal.primary};
    border: 1.5px solid ${theme.color.teal.secondary};
    padding: 7.5px 19.5px;
    background-color: ${theme.color.teal.quaternary};
  }
  ${theme.switch({
    selected: `
      color: ${theme.color.teal.primary};
      border: 1.5px solid ${theme.color.teal.secondary};
      padding: 7.5px 19.5px;
      background-color: ${theme.color.teal.quaternary};
  `,
  })}

  @media (max-width: ${theme.screen.mobile}) {
    font-size: 16px;
  }
  @media (max-width: ${theme.screen.small}) {
    font-size: 13.4px;
  }
`

const SelectEl = styled.div`
  max-width: 380px;
`
