import React from 'react'
import styled from 'styled-components'

import { theme } from '../theme'
import { Icon } from '../icons'

const ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

type Option = {
  label: string
  value: any
}

type Props = {
  values: Array<any> | void
  onChange: (args: Array<any>) => void
  disabled?: boolean
  options: Array<Option>
}

export const MultiSelectInput = ({ values, onChange, options }: Props) => {
  const _values = values || []
  const onClick = (value, isSelected) => {
    const cleaned = _values.filter((v) => v !== value)
    const newValues = isSelected ? cleaned : [...cleaned, value]
    onChange(newValues)
  }
  return (
    <MultiSelectEl>
      {options.map((option, idx) => {
        const isSelected = _values.includes(option.value)
        return (
          <SelectEl
            key={option.label}
            selected={isSelected}
            onClick={() => onClick(option.value, isSelected)}
          >
            <span className="letter">{ALPHABET[idx]}</span>
            <span className="content">{option.label}</span>
            {isSelected && <Icon.Tick color={theme.color.teal.primary} />}
          </SelectEl>
        )
      })}
    </MultiSelectEl>
  )
}

const SelectEl = styled.div`
  display: grid;
  grid-template-columns: 28px 1fr 18px;
  column-gap: 8px;
  justify-items: start;
  align-items: center;

  cursor: pointer;
  font-size: ${theme.text.subtitle};
  font-weight: 500;
  line-height: 28px;
  min-height: 46px;
  color: ${theme.color.teal.secondary};
  border: 1px solid ${theme.color.teal.tertiary};
  background-color: ${theme.color.teal.quinary};
  box-sizing: border-box;
  border-radius: 20px;
  padding: 8px 20px 8px 8px;
  & + & {
    margin-top: 8px;
  }
  .letter {
    align-self: start;
    font-size: 16px;
    width: 28px;
    height: 28px;
    display: inline-block;
    border-radius: 28px;
    background: ${theme.color.white};
    border: 1px solid ${theme.color.teal.tertiary};
    box-sizing: border-box;
    display: inline-flex;
    justify-content: center;
    align-items: center;
    flex-shrink: 0;
  }
  &:hover {
    box-shadow: ${theme.shadow};
    color: ${theme.color.teal.primary};
    border: 1.5px solid ${theme.color.teal.secondary};
    padding: 7.5px 19.5px 7.5px 7.5px;
    background-color: ${theme.color.teal.quaternary};
    .letter {
      border: none;
      color: ${theme.color.white};
      background-color: ${theme.color.teal.secondary};
    }
  }
  ${theme.switch({
    selected: `
      color: ${theme.color.teal.primary};
      border: 1.5px solid ${theme.color.teal.secondary};
      padding: 7.5px 19.5px 7.5px 7.5px;
      background-color: ${theme.color.teal.quaternary};
      .letter {
        border: none;
        color: ${theme.color.white};
        background-color: ${theme.color.teal.secondary};
      }
  `,
  })}

  @media (max-width: ${theme.screen.mobile}) {
    font-size: 16px;
  }
  @media (max-width: ${theme.screen.small}) {
    font-size: 13.4px;
  }
`

const MultiSelectEl = styled.div`
  min-width: 280px;
  max-width: 550px;
`
