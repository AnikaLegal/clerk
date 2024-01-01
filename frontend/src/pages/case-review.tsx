import React, { useState } from 'react'
import { Container, Header, Dropdown, Segment, Button } from 'semantic-ui-react'

import { CaseListTable } from 'comps/case-table'
import { mount } from 'utils'
import { Issue, useGetUsersQuery } from 'api'

interface DjangoContext {
  issues: Issue[]
}

const CONTEXT = (window as any).REACT_CONTEXT as DjangoContext

const TABLE_FIELDS = [
  'fileref',
  'topic',
  'client',
  'paralegal',
  'lawyer',
  'next_review',
  'created_at',
  'stage',
  'provided_legal_services',
]

const App = () => {
  const issues = CONTEXT.issues
  const [lawyer, setLawyer] = useState<number | null>(null)
  const lawyerResults = useGetUsersQuery({ group: 'Lawyer' })
  const filteredIssues = issues.filter(
    (i) => !lawyer || i.lawyer?.id === lawyer
  )
  return (
    <Container>
      <MissingChecksAlert issues={issues} />
      <Header as="h1">
        Case Review Queue
        <Header.Subheader>
          All open and assigned cases, sorted by next review date.
        </Header.Subheader>
      </Header>
      <Dropdown
        fluid
        selection
        clearable
        value={lawyer}
        loading={lawyerResults.isFetching}
        placeholder="Select a lawyer"
        options={lawyerResults.data?.map((u) => ({
          key: u.id,
          value: u.id,
          text: u.email,
        }))}
        onChange={(e, { value }) => setLawyer(value as number)}
      />
      <CaseListTable issues={filteredIssues} fields={TABLE_FIELDS} />
    </Container>
  )
}

const CHECKS_MISSING_TABLE_FIELDS = [
  'fileref',
  'topic',
  'client',
  'paralegal',
  'stage',
  'is_conflict_check',
  'is_eligibility_check',
]

interface MissingChecksAlertProps {
  issues: Issue[]
}

const MissingChecksAlert: React.FC<MissingChecksAlertProps> = ({ issues }) => {
  const [showMissing, setShowMissing] = useState<boolean>(false)
  const alertIssues = issues
    .filter((i) => i.stage !== 'UNSTARTED')
    .filter((i) => i.paralegal)
    .filter((i) => !(i.is_conflict_check && i.is_eligibility_check))

  return (
    <Segment
      inverted
      color="red"
      tertiary
      padded
      style={{ marginBottom: '3rem' }}
    >
      <Header as="h2">
        Checks Missing
        <Header.Subheader>
          {alertIssues.length} active cases are missing a conflict or
          eligibility check.
        </Header.Subheader>
      </Header>
      <Button color="red" onClick={() => setShowMissing(!showMissing)}>
        {showMissing ? 'Hide' : 'View'}
      </Button>
      {showMissing && (
        <CaseListTable
          issues={alertIssues}
          fields={CHECKS_MISSING_TABLE_FIELDS}
        />
      )}
    </Segment>
  )
}

mount(App)
