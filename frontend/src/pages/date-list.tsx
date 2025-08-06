import {
  Center,
  Container,
  Grid,
  Group,
  Loader,
  Pagination,
  Select,
  Table,
  Text,
  TextInput,
  Title,
} from '@mantine/core'
import { useDebouncedCallback } from '@mantine/hooks'
import { IconCheck, IconExclamationCircle, IconX } from '@tabler/icons-react'
import api, { GetCaseDatesApiArg, IssueDate, useGetCaseDatesQuery } from 'api'
import { RichTextDisplay } from 'comps/rich-text'
import { enqueueSnackbar } from 'notistack'
import React, { useEffect, useState } from 'react'
import { choiceToMap, getAPIErrorMessage, mount } from 'utils'

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

  const handleFilterChange = (key: keyof GetCaseDatesApiArg, value: any) => {
    setArgs((prevArgs) => ({
      ...prevArgs,
      [key]: value !== null ? value : undefined,
      page: 1, // Reset to first page on filter change
    }))
  }
  const debouncedFilterChange = useDebouncedCallback(
    (key: keyof GetCaseDatesApiArg, value: any) => {
      handleFilterChange(key, value)
    },
    300 // Adjust the debounce delay as needed
  )

  return (
    <Container size="xl">
      <Title order={1}>Critical Dates</Title>

      {!result.isLoading && result.data && (
        <Text c="dimmed">
          Showing {result.data.results.length} of {result.data.item_count}{' '}
          critical dates
        </Text>
      )}

      <Grid mt="lg">
        <Grid.Col span={12}>
          <TextInput
            size="md"
            label="Search"
            placeholder="Find dates with the name or email of clients or by using the file ref"
            onChange={(event) =>
              debouncedFilterChange('q', event.currentTarget.value)
            }
          />
        </Grid.Col>
        <Grid.Col span={6}>
          <Select
            clearable
            size="md"
            label="Date type"
            data={Types.map((choice) => ({
              value: choice[0],
              label: choice[1],
            }))}
            onChange={(value) => handleFilterChange('type', value)}
            withCheckIcon={false}
          />
        </Grid.Col>
        <Grid.Col span={6}>
          <Select
            clearable
            size="md"
            label="Reviewed?"
            data={[
              { value: 'true', label: 'Yes' },
              { value: 'false', label: 'No' },
            ]}
            onChange={(value) => handleFilterChange('isReviewed', value)}
            withCheckIcon={false}
            value={args.isReviewed?.toString() || ''}
          />
        </Grid.Col>
      </Grid>

      <Table
        withColumnBorders
        withTableBorder
        verticalSpacing="md"
        fz="md"
        mt="lg"
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
          <Table.Td>
            <Center>
              {date.is_reviewed ? (
                <IconCheck color="var(--mantine-color-green-6)" stroke={3} />
              ) : (
                <IconX color="var(--mantine-color-yellow-6)" stroke={3} />
              )}
            </Center>
          </Table.Td>
        </Table.Tr>
      ))}
    </>
  )
}

mount(App)
