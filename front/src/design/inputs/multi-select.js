// @flow
import React from 'react'
import styled from 'styled-components'

import { theme } from '../theme'
import { Icon } from '../shapes'

const ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

type Option = {
  label: string,
  value: any,
}

type Props = {
  values: Array<any> | void,
  onChange: (Array<any>) => void,
  disabled?: boolean,
  options: Array<Option>,
}

export const MultiSelectInput = ({
  values,
  onChange,
  disabled,
  options,
}: Props) => {
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
            <span>
              <span className="letter">{ALPHABET[idx]}</span>
              {option.label}{' '}
            </span>
            {isSelected && <Icon.Tick color={theme.color.teal.primary} />}
          </SelectEl>
        )
      })}
    </MultiSelectEl>
  )
}

const SelectEl = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: ${theme.text.subtitle};
  font-weight: 500;
  line-height: 28px;
  height: 46px;
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
    margin-right: 8px;
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
`

const MultiSelectEl = styled.div`
  width: 280px;
`
