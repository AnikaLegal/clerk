import { MantineColor, Table } from '@mantine/core'
import { IssueDate } from 'api'
import dayjs from 'dayjs'
import React from 'react'

export const DateTableDateCell = ({ date }: { date: IssueDate }) => {
  const d = dayjs(date.date, 'DD/MM/YYYY')
  const now = dayjs()
  let color: MantineColor = 'green.2'
  if (d.isBefore(now.add(7 + 1, 'day'), 'day')) {
    color = 'red.2'
  } else if (d.isBefore(now.add(14 + 1, 'day'), 'day')) {
    color = 'yellow.2'
  }
  return <Table.Td bg={color}>{date.date}</Table.Td>
}
