import { Badge, Table } from '@mantine/core'
import { IssueDate } from 'api'
import { CASE_DATE_HEARING_TYPES } from 'consts'
import React from 'react'

export const DateTableHearingTypeCell = ({ date }: { date: IssueDate }) => {
  return (
    <Table.Td>
      {date.hearing_type ? CASE_DATE_HEARING_TYPES[date.hearing_type] : '-'}
    </Table.Td>
  )
}
