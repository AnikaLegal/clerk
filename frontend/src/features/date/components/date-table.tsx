import { Center, Group, Loader, Table, Text } from '@mantine/core'
import { IconExclamationCircle } from '@tabler/icons-react'
import { IssueDate, useGetCaseDatesQuery } from 'api'
import { enqueueSnackbar } from 'notistack'
import React, { useEffect } from 'react'
import { getAPIErrorMessage } from 'utils'

interface DateTableProps {
  result: ReturnType<typeof useGetCaseDatesQuery>
  headerRow: React.ReactNode
  dataRow: React.ComponentType<{ date: IssueDate }>
}

export const DateTable = ({ result, headerRow, dataRow }: DateTableProps) => {
  return (
    <Table
      withColumnBorders
      withTableBorder
      verticalSpacing="md"
      fz="md"
      mt="lg"
    >
      <Table.Thead>{headerRow}</Table.Thead>
      <Table.Tbody>
        <DateTableBody result={result} dataRow={dataRow} />
      </Table.Tbody>
    </Table>
  )
}

const ErrorState = ({ error }: { error: any }) => {
  useEffect(() => {
    const message = getAPIErrorMessage(error, 'Could not load critical dates')
    enqueueSnackbar(message, { variant: 'error' })
  }, [error])

  return (
    <Table.Tr>
      <td colSpan={99}>
        <Group justify="center" gap="xs" m="sm" c="red">
          <IconExclamationCircle />
          <Text>Could not load critical dates</Text>
        </Group>
      </td>
    </Table.Tr>
  )
}

const LoadingState = () => (
  <Table.Tr>
    <td colSpan={99}>
      <Center m="sm">
        <Loader />
      </Center>
    </td>
  </Table.Tr>
)

const EmptyState = () => (
  <Table.Tr>
    <td colSpan={99}>
      <Center m="sm">No dates found</Center>
    </td>
  </Table.Tr>
)

interface DateTableBodyProps {
  result: ReturnType<typeof useGetCaseDatesQuery>
  dataRow: React.ComponentType<{ date: IssueDate }>
}

export const DateTableBody = ({ result, dataRow }: DateTableBodyProps) => {
  if (result.isError) {
    return <ErrorState error={result.error} />
  }
  if (result.isLoading) {
    return <LoadingState />
  }

  const data: IssueDate[] = result.data.results || []
  if (data.length < 1) {
    return <EmptyState />
  }

  const DataRow = dataRow
  return (
    <>
      {data.map((date) => (
        <DataRow key={date.id} date={date} />
      ))}
    </>
  )
}
