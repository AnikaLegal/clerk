import React from 'react'
import { Container, Header, Loader, Table } from 'semantic-ui-react'

import { mount, choiceToMap } from 'utils'
import { CaseHeader, CASE_TABS } from 'comps/case-header'
import api, { GetCaseServicesApiArg } from 'api'

interface DjangoContext {
  case_pk: string
  choices: {
    category: string[][]
    type_discrete: string[][]
    type_ongoing: string[][]
  }
  urls: {
    detail: string
    email: string
    docs: string
    services: string
  }
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
      <DiscreteCaseServiceTable args={{ id: case_id }}/>
      <Header as="h2">Ongoing services</Header>
      <OngoingCaseServiceTable args={{ id: case_id }}/>
    </Container>
  )
}

interface ServiceTableProps {
  args: GetCaseServicesApiArg
}

export const DiscreteCaseServiceTable: React.FC<ServiceTableProps> = ({
  args,
}) => {
  const servicesResult = api.useGetCaseServicesQuery({
    ...args,
    category: 'DISCRETE',
  })
  if (servicesResult.isLoading) {
    return <Loader active inline='centered' />
  }
  if (servicesResult.data.length == 0) {
    return <p>No discrete services</p>
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
        {servicesResult.data.map(({ id, type, started_at, count, note }) => (
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
  const servicesResult = api.useGetCaseServicesQuery({
    ...args,
    category: 'ONGOING',
  })
  if (servicesResult.isLoading) {
    return <Loader active inline='centered' />
  }
  if (servicesResult.data.length == 0) {
    return <p>No ongoing services</p>
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
        {servicesResult.data.map(({ id, type, started_at, finished_at, note }) => (
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
