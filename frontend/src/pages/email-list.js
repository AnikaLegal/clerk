import React, { useState, useEffect } from 'react'
import {
  Button,
  Container,
  Header,
  Table,
  Input,
  Dropdown,
  Label,
  Icon,
} from 'semantic-ui-react'
import { mount } from 'utils'
import { CaseHeader, CASE_TABS } from 'comps/case-header'

const { issue, email_threads, case_email_address, urls, draft_url } =
  window.REACT_CONTEXT

const App = () => {
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
          {email_threads.length < 1 && (
            <Table.Row>
              <td>No emails found</td>
            </Table.Row>
          )}
          {email_threads.map((t) => (
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
