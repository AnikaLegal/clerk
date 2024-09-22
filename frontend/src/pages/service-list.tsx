import React from 'react'
import {
  Container,
  Header,
  Loader,
  Segment,
  Table
} from 'semantic-ui-react'

import api, { GetCaseServicesApiArg } from 'api'
import { CASE_TABS, CaseHeader, CaseTabUrls } from 'comps/case-header'
import { choiceToMap, mount } from 'utils'

interface DjangoContext {
  case_pk: string
  choices: {
    category: string[][]
    type_discrete: string[][]
    type_ongoing: string[][]
  }
  urls: CaseTabUrls
}
const CONTEXT = (window as any).REACT_CONTEXT as DjangoContext
const DISCRETE_TYPE_LABELS = choiceToMap(CONTEXT.choices.type_discrete)
const ONGOING_TYPE_LABELS = choiceToMap(CONTEXT.choices.type_ongoing)

const App = () => {
  const case_id = CONTEXT.case_pk
  const urls = CONTEXT.urls

  const caseResult = api.useGetCaseQuery({ id: case_id })
  if (caseResult.isFetching) return null

  const issue = caseResult.data!.issue
  return (
    <Container>
      <CaseHeader issue={issue} activeTab={CASE_TABS.SERVICES} urls={urls} />
      <Header as="h2">Discrete services</Header>
      <Segment basic>
        <DiscreteCaseServiceTable args={{ id: case_id }} />
      </Segment>
      <Header as="h2">Ongoing services</Header>
      <Segment basic>
        <OngoingCaseServiceTable args={{ id: case_id }} />
      </Segment>
    </Container>
  )
}

interface ServiceTableProps {
  args: GetCaseServicesApiArg
}

export const DiscreteCaseServiceTable: React.FC<ServiceTableProps> = ({
  args,
}) => {
  const result = api.useGetCaseServicesQuery({
    ...args,
    category: 'DISCRETE',
  })
  if (result.isLoading) {
    return <Loader active inline="centered" />
  }
  if (result.data.length == 0) {
    return (
      <Segment textAlign="center" secondary>
        <p>No discrete services exist for this case.</p>
      </Segment>
    )
  }
  return (
    <Table celled fixed>
      <Table.Header>
        <Table.Row>
          <Table.HeaderCell>Type</Table.HeaderCell>
          <Table.HeaderCell>Date</Table.HeaderCell>
          <Table.HeaderCell>Count</Table.HeaderCell>
          <Table.HeaderCell>Notes</Table.HeaderCell>
        </Table.Row>
      </Table.Header>
      <Table.Body>
        {result.data.map(({ id, type, started_at, count, note }) => (
          <Table.Row key={id}>
            <Table.Cell>{DISCRETE_TYPE_LABELS.get(type)}</Table.Cell>
            <Table.Cell>{started_at}</Table.Cell>
            <Table.Cell>{count}</Table.Cell>
            <Table.Cell>{note}</Table.Cell>
          </Table.Row>
        ))}
      </Table.Body>
    </Table>
  )
}

export const OngoingCaseServiceTable: React.FC<ServiceTableProps> = ({
  args,
}) => {
  const result = api.useGetCaseServicesQuery({
    ...args,
    category: 'ONGOING',
  })
  if (result.isLoading) {
    return <Loader active inline="centered" />
  }
  if (result.data.length == 0) {
    return (
      <Segment textAlign="center" secondary>
        <p>No ongoing services exist for this case.</p>
      </Segment>
    )
  }
  return (
    <Table celled fixed>
      <Table.Header>
        <Table.Row>
          <Table.HeaderCell>Type</Table.HeaderCell>
          <Table.HeaderCell>Start date</Table.HeaderCell>
          <Table.HeaderCell>Finish date</Table.HeaderCell>
          <Table.HeaderCell>Notes</Table.HeaderCell>
        </Table.Row>
      </Table.Header>
      <Table.Body>
        {result.data.map(({ id, type, started_at, finished_at, note }) => (
          <Table.Row key={id}>
            <Table.Cell>{ONGOING_TYPE_LABELS.get(type)}</Table.Cell>
            <Table.Cell>{started_at}</Table.Cell>
            <Table.Cell>{finished_at}</Table.Cell>
            <Table.Cell>{note}</Table.Cell>
          </Table.Row>
        ))}
      </Table.Body>
    </Table>
  )
}

mount(App)
