import {
  Center,
  Container,
  Grid,
  Pagination,
  Table,
  Text,
  Title,
} from '@mantine/core'
import api, { GetCaseDatesApiArg, IssueDate } from 'api'
import { SelectFilter, TextInputFilter } from 'comps/filter'
import { CASE_DATE_TYPES } from 'consts'
import {
  DateActionIconGroup,
  DateTable,
  DateTableDateCell,
  DateTableHearingLocationCell,
  DateTableHearingTypeCell,
  DateTableIsReviewedCell,
  DateTableNotesCell,
  DateTableTypeCell,
} from 'features/date'
import React, { useState } from 'react'
import { UserPermission } from 'types'
import { mount } from 'utils'

interface DjangoContext {
  user: UserPermission
}
const CONTEXT = (window as any).REACT_CONTEXT as DjangoContext

const App = () => {
  const [args, setArgs] = useState<GetCaseDatesApiArg>({
    isReviewed: false,
    page: 1,
  })
  const result = api.useGetCaseDatesQuery(args)

  const handleFilterChange = (key, value) => {
    setArgs((prevArgs) => ({
      ...prevArgs,
      [key]: value !== null ? value : undefined,
      page: 1, // Reset to first page on filter change
    }))
  }

  const tableHeader = (
    <Table.Tr>
      <Table.Th>Fileref</Table.Th>
      <Table.Th>Client</Table.Th>
      <Table.Th>Date</Table.Th>
      <Table.Th>Type</Table.Th>
      <Table.Th>Hearing type</Table.Th>
      <Table.Th>Hearing location</Table.Th>
      <Table.Th>Notes</Table.Th>
      <Table.Th>Reviewed?</Table.Th>
      <Table.Th></Table.Th>
    </Table.Tr>
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
          <TextInputFilter
            name="q"
            label="Search"
            placeholder="Search by client name, email, or file ref"
            onFilterChange={handleFilterChange}
          />
        </Grid.Col>
        <Grid.Col span={6}>
          <SelectFilter
            name="type"
            data={Object.entries(CASE_DATE_TYPES).map((type) => ({
              value: type[0],
              label: type[1],
            }))}
            label="Date type"
            value={args.type || ''}
            onFilterChange={handleFilterChange}
          />
        </Grid.Col>
        <Grid.Col span={6}>
          <SelectFilter
            name="isReviewed"
            data={[
              { value: 'true', label: 'Yes' },
              { value: 'false', label: 'No' },
            ]}
            label="Reviewed?"
            value={args.isReviewed?.toString() || ''}
            onFilterChange={handleFilterChange}
          />
        </Grid.Col>
      </Grid>
      <DateTable
        result={result}
        headerRow={tableHeader}
        dataRow={DateTableDataRow}
      />
      {!result.isLoading && result.data && (
        <Pagination
          total={result.data.page_count}
          value={args.page || 1}
          onChange={(page) => setArgs({ ...args, page })}
          mt="md"
          withEdges
          withControls
        />
      )}
    </Container>
  )
}

const DateTableDataRow = ({ date }: { date: IssueDate }) => {
  return (
    <Table.Tr>
      <Table.Td>
        <a href={date.issue.url}>{date.issue.fileref}</a>
      </Table.Td>
      <Table.Td>
        <a href={date.issue.client.url}>{date.issue.client.full_name}</a>
      </Table.Td>
      <DateTableDateCell date={date} />
      <DateTableTypeCell date={date} />
      <DateTableHearingTypeCell date={date} />
      <DateTableHearingLocationCell date={date} />
      <DateTableNotesCell date={date} />
      <DateTableIsReviewedCell date={date} />
      <Table.Td>
        <Center>
          <DateActionIconGroup date={date} user={CONTEXT.user} />
        </Center>
      </Table.Td>
    </Table.Tr>
  )
}

mount(App)
