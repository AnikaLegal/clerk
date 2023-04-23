import React, { useState, useEffect } from 'react'
import styled from 'styled-components'
import moment from 'moment'

import { NumberInput } from './number'
import { theme } from '../theme'

type Props = {
  value: string | void
  onChange: (string) => void
  disabled?: boolean
  onFocus?: Function
  onBlur?: Function
  autoFocus?: boolean
}

export const DateInput = ({
  onChange,
  value,
  disabled,
  onFocus,
  onBlur,
  autoFocus,
}: Props) => {
  const date = getDateFromString(value)
  const [isValid, setValid] = useState(Boolean(date))
  const [day, setDay] = useState<number | null>(null)
  const [month, setMonth] = useState<number | null>(null)
  const [year, setYear] = useState<number | null>(null)
  useEffect(() => {
    if (date) {
      setDay(date.get('date'))
      setMonth(date.get('month') + 1)
      setYear(date.get('year'))
    }
  }, [value])

  const onDayChange = (val) => {
    const newDay = Number(val)
    if (newDay > 31) return
    const newDate = getDateFromVals(year, month, newDay)
    setDay(newDay)
    if (newDate) {
      onChange(getStringFromDate(newDate))
      setValid(true)
    } else {
      setValid(false)
      onChange('')
    }
  }
  const onMonthChange = (val) => {
    const newMonth = Number(val)
    if (newMonth > 12) return
    const newDate = getDateFromVals(year, newMonth, day)
    setMonth(newMonth)
    if (newDate) {
      onChange(getStringFromDate(newDate))
      setValid(true)
    } else {
      setValid(false)
      onChange('')
    }
  }
  const onYearChange = (val) => {
    const newYear = Number(val)
    if (newYear > new Date().getFullYear() + 3) return
    const newDate = getDateFromVals(newYear, month, day)
    setYear(newYear)
    if (newDate) {
      onChange(getStringFromDate(newDate))
      setValid(true)
    } else {
      setValid(false)
      onChange('')
    }
  }
  const isInvalid = !isValid && Boolean(day || month || year)
  return (
    <DateFieldEl>
      <NumberInput
        placeholder="DD"
        disabled={disabled}
        onChange={onDayChange}
        value={day || ''}
        onFocus={onFocus}
        onBlur={onBlur}
        style={{ width: '50px' }}
        autoFocus={autoFocus}
      />
      <Separator invalid={isInvalid}>/</Separator>
      <NumberInput
        placeholder="MM"
        disabled={disabled}
        onChange={onMonthChange}
        value={month || ''}
        onFocus={onFocus}
        onBlur={onBlur}
        style={{ width: '59px' }}
      />
      <Separator invalid={isInvalid}>/</Separator>
      <NumberInput
        placeholder="YYYY"
        disabled={disabled}
        onChange={onYearChange}
        value={year || ''}
        onFocus={onFocus}
        onBlur={onBlur}
        style={{ width: '80px' }}
      />
    </DateFieldEl>
  )
}

const getStringFromDate = (date) => date.format('YYYY-MM-DD')

const getDateFromString = (s) => {
  if (!s) return null
  return moment(s, 'YYYY-MM-DD')
}

const getDateFromVals = (
  y: number | null,
  m: number | null,
  d: number | null
) => {
  if (!d || !m || !y) return null
  const newMoment = moment([y, m, d].join('-'), 'Y-M-D')
  if (!newMoment.isValid()) {
    return null
  } else {
    return newMoment
  }
}

const DateFieldEl = styled.div`
  input {
    display: inline-block;
    text-align: center;
    font-size: 30px;
    padding: 0 0 12px 0;
    border-radius: 0;
  }
  &:not(:hover) {
    input:first-child {
      border-bottom: 2px solid ${theme.color.teal.primary};
    }
  }
`
const Separator = styled.div`
  margin: 0 3px;
  display: inline-block;
  font-size: 30px;
  color: ${theme.color.teal.primary};
`
