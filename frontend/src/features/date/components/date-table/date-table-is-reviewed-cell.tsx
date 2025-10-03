import { Center, Table } from '@mantine/core'
import { IconCheck, IconX } from '@tabler/icons-react'
import { IssueDate } from 'api'
import React from 'react'

export const DateTableIsReviewedCell = ({ date }: { date: IssueDate }) => {
  return (
    <Table.Td>
      <Center>
        {date.is_reviewed ? (
          <IconCheck color="var(--mantine-color-green-6)" stroke={3} />
        ) : (
          <IconX color="var(--mantine-color-yellow-6)" stroke={3} />
        )}
      </Center>
    </Table.Td>
  )
}
