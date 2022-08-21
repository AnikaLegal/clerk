import React, { useState } from 'react'
import { Container, Header, Button, Tab } from 'semantic-ui-react'
import moment from 'moment'
import * as Yup from 'yup'

import { TimelineNote } from 'comps/timeline-item'
import { TableForm } from 'comps/table-form'
import { getFormSchema, FIELD_TYPES } from 'comps/auto-form'
import { CaseListTable } from 'comps/case-table'
import { mount } from 'utils'
import { api } from 'api'
import { AccountPermissions } from 'comps/account-permissions'
import { ErrorBoundary } from 'comps/error-boundary'

const creationSort = (a, b) =>
  moment(b.created_at, 'DD/MM/YY').unix() -
  moment(a.created_at, 'DD/MM/YY').unix()

const App = () => {
  const [account, setAccount] = useState(window.REACT_CONTEXT.account)
  let tabPanes = [
    {
      menuItem: 'Paralegal cases',
      render: () => (
        <Tab.Pane>
          <CaseListTable
            issues={account.issue_set.sort(creationSort)}
            fields={PARALEGAL_TABLE_FIELDS}
          />
        </Tab.Pane>
      ),
    },
    {
      menuItem: 'Lawyer cases',
      render: () => (
        <Tab.Pane>
          <CaseListTable
            issues={account.lawyer_issues.sort(creationSort)}
            fields={LAWYER_TABLE_FIELDS}
          />
        </Tab.Pane>
      ),
    },
    {
      menuItem: 'Performance notes',
      render: () => (
        <Tab.Pane>
          {account.performance_notes.length < 1 && 'No notes yet'}
          {account.performance_notes.map((note) => (
            <TimelineNote note={note} key={note.id} />
          ))}
        </Tab.Pane>
      ),
    },
    {
      menuItem: 'Permissions',
      render: () => (
        <Tab.Pane>
          <ErrorBoundary>
            <AccountPermissions account={account} setAccount={setAccount} />
          </ErrorBoundary>
        </Tab.Pane>
      ),
    },
  ]
  // Prioritise lawyer issues if they exist
  if (account.lawyer_issues.length > 0) {
    tabPanes = [tabPanes[1], tabPanes[0], tabPanes[2], tabPanes[3]]
  }
  if (!account.is_coordinator_or_better) {
    // Don't show lawyer cases.
    tabPanes = [tabPanes[0], tabPanes[2], tabPanes[3]]
  }
  return (
    <Container>
      <Header as="h1" disabled={!account.is_active}>
        {account.full_name} {!account.is_active && ' (inactive)'}
        <Header.Subheader>{account.email}</Header.Subheader>
      </Header>
      <Header as="h3">User details</Header>
      <TableForm
        fields={FIELDS}
        schema={SCHEMA}
        model={account}
        setModel={setAccount}
        modelName="account"
        onUpdate={api.accounts.update}
      />

      <Tab style={{ marginTop: '2em' }} panes={tabPanes} />
    </Container>
  )
}

const PARALEGAL_TABLE_FIELDS = [
  'fileref',
  'topic',
  'client',
  'lawyer',
  'created_at',
  'stage',
  'provided_legal_services',
  'outcome',
]
const LAWYER_TABLE_FIELDS = [
  'fileref',
  'topic',
  'client',
  'paralegal',
  'created_at',
  'stage',
  'provided_legal_services',
  'outcome',
]

const FIELDS = [
  {
    label: 'First name',
    schema: Yup.string().required('Required'),
    type: FIELD_TYPES.TEXT,
    name: 'first_name',
  },
  {
    label: 'Last name',
    schema: Yup.string().required('Required'),
    type: FIELD_TYPES.TEXT,
    name: 'last_name',
  },
  {
    label: 'Is Intern',
    name: 'is_intern',
    type: FIELD_TYPES.BOOL,
    schema: Yup.string().required('Required'),
  },
  {
    label: 'Case capacity',
    type: FIELD_TYPES.TEXT,
    name: 'case_capacity',
    schema: Yup.number().integer().min(0),
  },
  {
    label: 'Active',
    type: FIELD_TYPES.BOOL,
    name: 'is_active',
    schema: Yup.boolean(),
  },
]
const SCHEMA = getFormSchema(FIELDS)

mount(App)
