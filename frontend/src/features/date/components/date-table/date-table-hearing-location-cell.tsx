import { Table } from '@mantine/core'
import { IssueDate } from 'api'
import { RichTextDisplay } from 'comps/rich-text'
import React from 'react'

export const DateTableHearingLocationCell = ({ date }: { date: IssueDate }) => {
  return (
    <Table.Td maw="300px">
      {date.hearing_location ? (
        <RichTextDisplay content={date.hearing_location} />
      ) : (
        '-'
      )}
    </Table.Td>
  )
}
