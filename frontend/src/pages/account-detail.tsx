import React, { useState } from 'react'
import { Container, Header, Tab } from 'semantic-ui-react'
import moment from 'moment'
import * as Yup from 'yup'

import { TimelineNote } from 'comps/timeline-item'
import { TableForm } from 'comps/table-form'
import { getFormSchema, FormField } from 'comps/auto-form'
import { CaseListTable } from 'comps/case-table'
import { mount } from 'utils'
import { AccountPermissions } from 'comps/account-permissions'
import { ErrorBoundary } from 'comps/error-boundary'
import { FIELD_TYPES } from 'comps/field-component'
import { User, UserCreate, useUpdateUserMutation } from 'api'

interface DjangoContext {
  account: User
  issue_set: any[]
  lawyer_issues: any[]
  performance_notes: any[]
}

const CONTEXT = (window as any).REACT_CONTEXT as DjangoContext

const App = () => {
  const [account, setAccount] = useState(CONTEXT.account)
  const [updateUser] = useUpdateUserMutation()
  const update = (id: string, values: { [fieldName: string]: unknown }) =>
    updateUser({
      id: account.id,
      userCreate: values as UserCreate,
    }).unwrap()

  let tabPanes = [
    {
      menuItem: 'Paralegal cases',
      render: () => (
        <Tab.Pane>
          <CaseListTable
            issues={CONTEXT.issue_set.sort(creationSort)}
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
            issues={CONTEXT.lawyer_issues.sort(creationSort)}
            fields={LAWYER_TABLE_FIELDS}
          />
        </Tab.Pane>
      ),
    },
    {
      menuItem: 'Performance notes',
      render: () => (
        <Tab.Pane>
          {CONTEXT.performance_notes.length < 1 && 'No notes yet'}
          {CONTEXT.performance_notes.map((note) => (
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
  if (CONTEXT.lawyer_issues.length > 0) {
    tabPanes = [tabPanes[1], tabPanes[0], tabPanes[2], tabPanes[3]]
  }
  if (CONTEXT.lawyer_issues.length === 0) {
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
        onUpdate={update}
      />

      <Tab style={{ marginTop: '2em' }} panes={tabPanes} />
    </Container>
  )
}

const creationSort = (a: any, b: any) =>
  moment(b.created_at, 'DD/MM/YY').unix() -
  moment(a.created_at, 'DD/MM/YY').unix()

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

const FIELDS: FormField[] = [
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
