import {
  Center,
  Container,
  Group,
  Loader,
  Pagination,
  Table,
  Text,
  Title,
} from '@mantine/core'
import { IconExclamationCircle } from '@tabler/icons-react'
import api, { GetCaseDatesApiArg, IssueDate, useGetCaseDatesQuery } from 'api'
import { enqueueSnackbar } from 'notistack'
import React, { useEffect, useState } from 'react'
import { choiceToMap, getAPIErrorMessage, mount } from 'utils'
import { RichTextDisplay } from 'comps/rich-text'

import '@mantine/core/styles.css'

interface DjangoContext {
  choices: {
    type: [string, string][]
  }
}
const CONTEXT = (window as any).REACT_CONTEXT as DjangoContext
const Types = CONTEXT.choices.type.sort((a, b) => a[1].localeCompare(b[1]))
const TypeLabels = choiceToMap(Types)

const App = () => {
  const [args, setArgs] = useState<GetCaseDatesApiArg>({
    isReviewed: false,
    page: 1,
  })
  const result = api.useGetCaseDatesQuery(args)

  return (
    <Container size="xl">
      <Title order={1}>Critical Dates</Title>
      {!result.isLoading && result.data && (
        <Text c="dimmed">
          Showing {result.data.results.length} of {result.data.item_count}{' '}
          critical dates
        </Text>
      )}
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
            <Table.Th>Type</Table.Th>
            <Table.Th>Critical date</Table.Th>
            <Table.Th>Client</Table.Th>
            <Table.Th>Notes</Table.Th>
            <Table.Th>Reviewed?</Table.Th>
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>
          <CriticalDatesTableBody result={result} />
        </Table.Tbody>
      </Table>
      {!result.isLoading && result.data && (
        <Pagination
          total={result.data.page_count}
          onChange={(page) => setArgs({ ...args, page })}
          mt="md"
          withEdges
          withControls
        />
      )}
    </Container>
  )
}

const ErrorState = ({ error }: { error: any }) => {
  useEffect(() => {
    const message = getAPIErrorMessage(error, 'Could not load critical dates')
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

  const data: IssueDate[] = result.data.results || []
  if (data.length < 1) {
    return <EmptyState />
  }

  return (
    <>
      {data.map((date) => (
        <Table.Tr key={date.id}>
          <Table.Td>
            <a href={date.issue.url}>{date.issue.fileref}</a>
          </Table.Td>
          <Table.Td>{TypeLabels.get(date.type)}</Table.Td>
          <Table.Td>{date.date}</Table.Td>
          <Table.Td>
            <a href={date.issue.client.url}>{date.issue.client.full_name}</a>
          </Table.Td>
          <Table.Td>
            <RichTextDisplay content={date.notes} />
          </Table.Td>
          <Table.Td>{date.is_reviewed ? 'Yes' : 'No'}</Table.Td>
        </Table.Tr>
      ))}
    </>
  )
}

mount(App)
