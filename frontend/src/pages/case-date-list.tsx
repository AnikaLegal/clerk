import {
  Center,
  Container,
  Pagination,
  Table,
  Text,
  Title,
} from '@mantine/core'
import api, { GetCaseDatesApiArg, Issue, IssueDate } from 'api'
import { CASE_TABS, CaseHeader, CaseTabUrls } from 'comps/case-header'
import { RichTextDisplay } from 'comps/rich-text'
import {
  DateActionIconGroup,
  DateTable,
  DateTableDateCell,
  DateTableIsReviewedCell,
  DateTableTypeCell,
} from 'features/date'
import React, { useState } from 'react'
import { UserPermission } from 'types'
import { mount } from 'utils'

import '@mantine/core/styles.css'

interface DjangoContext {
  case_pk: string
  urls: CaseTabUrls
  user: UserPermission
}
const CONTEXT = (window as any).REACT_CONTEXT as DjangoContext

const App = () => {
  const caseId = CONTEXT.case_pk
  const urls = CONTEXT.urls

  const result = api.useGetCaseQuery({ id: caseId })
  if (result.isFetching || !result.data) {
    return null
  }
  const issue = result.data.issue

  return (
    <Container size="xl">
      <CaseHeader issue={issue} activeTab={CASE_TABS.DATES} urls={urls} />
      <Title order={2} mt="xl">
        Critical Dates
      </Title>
      <CaseDateTable issue={issue} />
    </Container>
  )
}

interface CaseDateTableProps {
  issue: Issue
}

const CaseDateTable = ({ issue }: CaseDateTableProps) => {
  const [args, setArgs] = useState<GetCaseDatesApiArg>({
    issueId: issue.id,
    page: 1,
  })
  const result = api.useGetCaseDatesQuery(args)

  const headerRow = (
    <Table.Tr>
      <Table.Th>Type</Table.Th>
      <Table.Th>Date</Table.Th>
      <Table.Th>Notes</Table.Th>
      <Table.Th>Reviewed?</Table.Th>
      <Table.Th></Table.Th>
    </Table.Tr>
  )

  return (
    <>
      {!result.isLoading && result.data && (
        <Text c="dimmed">
          Showing {result.data.results.length} of {result.data.item_count}{' '}
          critical dates
        </Text>
      )}
      <DateTable
        result={result}
        headerRow={headerRow}
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
    </>
  )
}

const DateTableDataRow = ({ date }: { date: IssueDate }) => {
  return (
    <Table.Tr>
      <DateTableTypeCell date={date} />
      <DateTableDateCell date={date} />
      <Table.Td>
        <RichTextDisplay content={date.notes} />
      </Table.Td>
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
