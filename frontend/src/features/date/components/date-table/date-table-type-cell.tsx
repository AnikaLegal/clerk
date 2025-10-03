import { Table } from '@mantine/core'
import { IssueDate } from 'api'
import { CASE_DATE_TYPES } from 'consts'
import React from 'react'

export const DateTableTypeCell = ({ date }: { date: IssueDate }) => {
  return <Table.Td>{CASE_DATE_TYPES[date.type]}</Table.Td>
}
