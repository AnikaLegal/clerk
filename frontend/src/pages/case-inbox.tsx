import React from 'react'
import { Container, Header } from 'semantic-ui-react'

import { CaseListTable } from 'comps/case-table'
import { mount } from 'utils'
import { Issue } from 'apiNew'

interface DjangoContext {
  issues: Issue[]
}

const CONTEXT = (window as any).REACT_CONTEXT as DjangoContext

const TABLE_FIELDS = [
  'fileref',
  'topic',
  'client',
  'paralegal',
  'created_at',
  'stage',
  'provided_legal_services',
  'is_conflict_check',
  'is_eligibility_check',
]

const App = () => {
  const issues = CONTEXT.issues
  return (
    <Container>
      <Header as="h1">
        Case Inbox
        <Header.Subheader>
          {issues.length} cases are open and have not yet been assigned to a
          paralegal.
        </Header.Subheader>
      </Header>
      <CaseListTable issues={issues} fields={TABLE_FIELDS} />
    </Container>
  )
}

mount(App)
