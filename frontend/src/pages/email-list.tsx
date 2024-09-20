import React from 'react'
import {
  Button,
  Container,
  Header,
  Table,
  Label,
  Icon,
} from 'semantic-ui-react'

import { mount } from 'utils'
import { CaseHeader, CASE_TABS } from 'comps/case-header'
import { useGetCaseQuery, useGetEmailThreadsQuery } from 'api'

interface DjangoContext {
  case_pk: string
  draft_url: string
  case_email_address: string
  urls: {
    detail: string
    email: string
    docs: string
    services: string
  }
}

const { case_pk, case_email_address, urls, draft_url } = (window as any)
  .REACT_CONTEXT as DjangoContext

const App = () => {
  const caseResult = useGetCaseQuery({ id: case_pk })
  const threadResult = useGetEmailThreadsQuery({ id: case_pk })

  if (caseResult.isLoading || threadResult.isLoading)
    return null

  const issue = caseResult.data!.issue
  const emailThreads =
    threadResult.isError && threadResult.error.status === 404 ? [] :
    threadResult.data

  return (
    <Container>
      <CaseHeader issue={issue} activeTab={CASE_TABS.EMAIL} urls={urls} />
      <Header as="h1">
        Case emails
        <Header.Subheader>
          You can contact this mailbox at: <strong>{case_email_address}</strong>
          <br />
          Emails are grouped into threads by subject line <strong>only</strong>.
          Please verify senders and recipients when reading and sending emails.
        </Header.Subheader>
      </Header>
      <a href={draft_url}>
        <Button primary>New Draft</Button>
      </a>
      <Table celled>
        <Table.Header>
          <Table.Row>
            <Table.HeaderCell>Subject</Table.HeaderCell>
            <Table.HeaderCell>Most recent</Table.HeaderCell>
            <Table.HeaderCell>Details</Table.HeaderCell>
          </Table.Row>
        </Table.Header>
        <Table.Body>
          {emailThreads.length < 1 && (
            <Table.Row>
              <td>No emails found</td>
            </Table.Row>
          )}
          {emailThreads.map((t) => (
            <Table.Row key={t.url}>
              <Table.Cell>
                <a href={t.url}>{t.subject}</a>
              </Table.Cell>
              <Table.Cell>{t.most_recent}</Table.Cell>
              <Table.Cell>
                {countEmailType(t.emails, 'DRAFT') > 0 && (
                  <Label color="blue">
                    <Icon name="mail" />
                    {countEmailType(t.emails, 'DRAFT')} drafts
                  </Label>
                )}
                {countEmailType(t.emails, 'DELIVERED') > 0 && (
                  <Label>
                    <Icon name="mail" />
                    {countEmailType(t.emails, 'DELIVERED')} sent
                  </Label>
                )}
                {countEmailType(t.emails, 'DELIVERY_FAILURE') > 0 && (
                  <Label color="red">
                    <Icon name="mail" />
                    {countEmailType(t.emails, 'DELIVERY_FAILURE')} failed
                  </Label>
                )}
                {countEmailType(t.emails, 'SENT') > 0 && (
                  <Label>
                    <Icon name="mail" />
                    {countEmailType(t.emails, 'SENT')} sending
                  </Label>
                )}
                {countEmailType(t.emails, 'INGESTED') > 0 && (
                  <Label>
                    <Icon name="mail" />
                    {countEmailType(t.emails, 'INGESTED')} received
                  </Label>
                )}
              </Table.Cell>
            </Table.Row>
          ))}
        </Table.Body>
      </Table>
    </Container>
  )
}

const countEmailType = (emails, state) =>
  emails.filter((e) => e.state === state).length

mount(App)
