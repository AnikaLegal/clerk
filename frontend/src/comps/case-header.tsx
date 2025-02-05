import React from 'react'
import { Header, Icon, Menu } from 'semantic-ui-react'

import { Issue } from 'api'
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
        <div className="sub header">
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
        </div>
      </Header>
      <span id="case-status" hx-swap-oob="true">
        {issue.is_open ? (
          <div className="ui blue label">Case open</div>
        ) : (
          <div className="ui green label">Case closed</div>
        )}
        {issue.provided_legal_services ? (
          <div className="ui green label">Legal services provided</div>
        ) : (
          <div className="ui blue label">Legal services not provided</div>
        )}

        <div className="ui grey label">
          Stage
          {issue.stage ? (
            <div className="detail">{issue.stage_display}</div>
          ) : (
            <div className="detail">-</div>
          )}
        </div>

        <div className="ui grey label">
          Outcome
          {issue.outcome ? (
            <div className="detail">{issue.outcome_display}</div>
          ) : (
            <div className="detail">-</div>
          )}
        </div>
        {!issue.is_open && issue.outcome_notes && (
          <div className="ui segment padded">
            <div className="ui top attached label green">Outcome notes</div>
            <p style={{ marginBottom: 0 }}>{issue.outcome_notes}</p>
          </div>
        )}
        {issue.client.notes && (
          <div className="ui segment padded">
            <div className="ui top attached label">Client notes</div>
            <MarkdownAsHtmlDisplay markdown={issue.client.notes} />
          </div>
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
