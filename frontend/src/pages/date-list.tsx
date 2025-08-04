import {
  Center,
  Container,
  Group,
  Loader,
  Table,
  Text,
  Title,
} from '@mantine/core'
import { IconExclamationCircle } from '@tabler/icons-react'
import api, { IssueDate, useGetCaseDatesQuery } from 'api'
import { enqueueSnackbar } from 'notistack'
import React, { useEffect } from 'react'
import { getAPIErrorMessage, mount } from 'utils'

import '@mantine/core/styles.css'

interface DjangoContext {}
const CONTEXT = (window as any).REACT_CONTEXT as DjangoContext

const App = () => {
  const result = api.useGetCaseDatesQuery({ isReviewed: false })
  return (
    <Container size="xl">
      <Title order={1}>Critical Dates</Title>
      <Table
        withColumnBorders
        withTableBorder
        verticalSpacing="md"
        fz="md"
        mt="md"
      >
        <Table.Thead>
          <Table.Tr>
            <Table.Th>Fileref</Table.Th>
            <Table.Th>Critical date</Table.Th>
            <Table.Th>Type</Table.Th>
            <Table.Th>Client</Table.Th>
            <Table.Th>Notes</Table.Th>
            <Table.Th>Reviewed?</Table.Th>
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>
          <CriticalDatesTableBody result={result} />
        </Table.Tbody>
      </Table>
    </Container>
  )
}

const ErrorState = ({ error }: { error: any }) => {
  useEffect(() => {
    const message = getAPIErrorMessage(error, 'Could not load email templates')
    enqueueSnackbar(message, { variant: 'error' })
  }, [error])

  return (
    <Table.Tr>
      <td colSpan={5}>
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
    <td colSpan={5}>
      <Center m="sm">
        <Loader />
      </Center>
    </td>
  </Table.Tr>
)

const EmptyState = () => (
  <Table.Tr>
    <td colSpan={5}>
      <Center m="sm">No dates found</Center>
    </td>
  </Table.Tr>
)

interface CriticalDatesTableBodyProps {
  result: ReturnType<typeof useGetCaseDatesQuery>
}

const CriticalDatesTableBody = ({ result }: CriticalDatesTableBodyProps) => {
  if (result.isError) {
    return <ErrorState error={result.error} />
  }
  if (result.isLoading) {
    return <LoadingState />
  }

  const data: IssueDate[] = result.data || []
  if (data.length < 1) {
    return <EmptyState />
  }

  return (
    <>
      {data.map((date) => (
        <Table.Tr key={date.issue.fileref}>
          <Table.Td>
            <a href={date.issue.url}>{date.issue.fileref}</a>
          </Table.Td>
          <Table.Td>{date.date}</Table.Td>
          <Table.Td>{date.type}</Table.Td>
          <Table.Td>
            <a href={date.issue.client.url}>{date.issue.client.full_name}</a>
          </Table.Td>
          <Table.Td>{date.notes}</Table.Td>
          <Table.Td>{date.is_reviewed ? 'Yes' : 'No'}</Table.Td>
        </Table.Tr>
      ))}
    </>
  )
}

mount(App)
