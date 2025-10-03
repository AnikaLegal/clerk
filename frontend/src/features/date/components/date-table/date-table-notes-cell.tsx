import { Table } from '@mantine/core'
import { IssueDate } from 'api'
import { RichTextDisplay } from 'comps/rich-text'
import React from 'react'

export const DateTableNotesCell = ({ date }: { date: IssueDate }) => {
  return (
    <Table.Td maw="300px">
      {date.notes && <RichTextDisplay content={date.notes} />}
    </Table.Td>
  )
}
