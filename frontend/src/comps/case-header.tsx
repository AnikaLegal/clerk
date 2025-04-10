import { Client, Issue } from 'api'
import React from 'react'
import { Header, Icon, Label, Menu, Segment } from 'semantic-ui-react'
import { MarkdownAsHtmlDisplay } from 'utils'

export const CASE_TABS = {
  DETAIL: 'DETAIL',
  EMAIL: 'EMAIL',
  DOCUMENTS: 'DOCUMENTS',
  SERVICES: 'SERVICES',
  TASKS: 'TASKS',
}

export interface CaseTabUrls {
  detail: string
  email: string
  docs: string
  services: string
  tasks: string
}

interface CaseHeaderProps {
  issue: Issue
  activeTab: string
  urls: CaseTabUrls
}

export const CaseHeader: React.FC<CaseHeaderProps> = ({
  issue,
  activeTab,
  urls,
}) => {
  const actionstepUrl = issue.actionstep_id
    ? `https://ap-southeast-2.actionstep.com/mym/asfw/workflow/action/overview/action_id/${issue.actionstep_id}"`
    : null

  return (
    <>
      <Header as="h1">
        {issue.topic_display} case for {issue.client.full_name} ({issue.fileref}
        )
        <Header.Subheader>
          Created {issue.created_at}
          <br />
          {issue.paralegal ? (
            <span>
              Assigned to{' '}
              <a href={issue.paralegal.url}>{issue.paralegal.full_name}</a>
              {', '}
            </span>
          ) : (
            'Not assigned, '
          )}
          {issue.lawyer ? (
            <span>
              supervised by{' '}
              <a href={issue.lawyer.url}>{issue.lawyer.full_name}</a>{' '}
            </span>
          ) : (
            'not supervised '
          )}
          {actionstepUrl && <a href={actionstepUrl}>view in Actionstep</a>}
        </Header.Subheader>
      </Header>
      <span id="case-status" hx-swap-oob="true">
        {issue.is_open ? (
          <Label color="blue">Case open</Label>
        ) : (
          <Label color="green">Case closed</Label>
        )}

        {issue.provided_legal_services ? (
          <Label color="green">Legal services provided</Label>
        ) : (
          <Label color="blue">Legal services not provided</Label>
        )}

        <Label color="grey">
          Stage
          <Label.Detail>{issue.stage ? issue.stage_display : '-'}</Label.Detail>
        </Label>

        <Label color="grey">
          Outcome
          <Label.Detail>
            {issue.outcome ? issue.outcome_display : '-'}
          </Label.Detail>
        </Label>

        {/* NOTE: Should always be between the labels & segments i.e. don't put
        a segment above or a label below. */}
        <MaybeContactRestrictionNotes client={issue.client} />

        {!issue.is_open && issue.outcome_notes && (
          <Segment padded>
            <Label attached="top" color="green">
              Outcome notes
            </Label>
            <p style={{ marginBottom: 0 }}>{issue.outcome_notes}</p>
          </Segment>
        )}

        {issue.client.notes && (
          <Segment padded>
            <Label attached="top">Client notes</Label>
            <MarkdownAsHtmlDisplay markdown={issue.client.notes} />
          </Segment>
        )}
      </span>
      <Menu attached="top" tabular>
        <Menu.Item
          as="a"
          href={urls.detail}
          active={activeTab === CASE_TABS.DETAIL}
        >
          <Icon name="clipboard outline" />
          Details
        </Menu.Item>
        <Menu.Item
          as="a"
          href={urls.email}
          active={activeTab === CASE_TABS.EMAIL}
        >
          <Icon name="envelope outline" />
          Email
        </Menu.Item>
        <Menu.Item
          as="a"
          href={urls.docs}
          active={activeTab === CASE_TABS.DOCUMENTS}
        >
          <Icon name="folder open outline" />
          Documents
        </Menu.Item>
        <Menu.Item
          as="a"
          href={urls.services}
          active={activeTab === CASE_TABS.SERVICES}
        >
          <Icon name="balance scale" />
          Services
        </Menu.Item>
        <Menu.Item
          as="a"
          href={urls.tasks}
          active={activeTab === CASE_TABS.TASKS}
        >
          <Icon name="check square outline" />
          Tasks
        </Menu.Item>
      </Menu>
    </>
  )
}

interface MaybeContactRestrictionNotesProps {
  client: Client
}

const MaybeContactRestrictionNotes = ({
  client,
}: MaybeContactRestrictionNotesProps) => {
  const status = client.contact_restriction
  const notes = client.contact_notes

  if (notes) {
    return (
      <Segment padded>
        <Label color="orange" attached="top">
          {status.value ? status.display : 'Contact notes'}
        </Label>
        <p>{notes}</p>
      </Segment>
    )
  }
  if (status.value) {
    return <Label color="orange">{status.display}</Label>
  }
  return null
}
