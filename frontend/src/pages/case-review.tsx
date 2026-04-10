import { Alert, Button, Container, Text, Title } from '@mantine/core'
import { useToggle } from '@mantine/hooks'
import { Issue } from 'api'
import { CaseListTable } from 'comps/case-table'
import { UserSelect } from 'comps/user-select'
import React, { useState } from 'react'
import { mount } from 'utils'

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
  const issuesByLawyer = issues.filter(
    (i) => !lawyer || i.lawyer?.id === lawyer
  )
  return (
    <Container size="xl">
      <MissingChecksAlert issues={issues} />
      <Title order={1} mt="xl">
        Case Review Queue
        <Text c="dimmed">
          All open and assigned cases, sorted by next review date.
        </Text>
      </Title>
      <UserSelect
        label="Lawyer"
        placeholder="Only show the cases supervised by the selected lawyer"
        onChange={(value) => setLawyer(Number(value) || null)}
        filter={{
          group: 'Lawyer',
          sort: 'email',
        }}
        mt="md"
      />
      <CaseListTable issues={issuesByLawyer} fields={TABLE_FIELDS} />
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

const MissingChecksAlert = ({ issues }: MissingChecksAlertProps) => {
  const [hideAlert, setHideAlert] = useState(false)
  const [showMissing, toggleMissing] = useToggle()

  const issuesWithMissingChecks = issues
    .filter((i) => i.stage !== 'UNSTARTED')
    .filter((i) => i.paralegal)
    .filter((i) => !(i.is_conflict_check && i.is_eligibility_check))
  const hasMissingChecks = issuesWithMissingChecks.length > 0

  if (hideAlert) return null

  return (
    <Alert
      autoContrast
      withCloseButton
      variant="filled"
      color={hasMissingChecks ? 'red' : 'green'}
      p="lg"
      onClose={() => setHideAlert(true)}
    >
      <Title order={2}>
        Checks Missing
        <Text>
          {issuesWithMissingChecks.length > 1
            ? `${issuesWithMissingChecks.length} active cases are`
            : issuesWithMissingChecks.length == 1
              ? 'One active case is'
              : 'No active cases are'}{' '}
          missing a conflict or eligibility check.
        </Text>
      </Title>
      {hasMissingChecks && (
        <>
          <Button
            variant="filled"
            color="red.8"
            onClick={() => toggleMissing()}
            mt="md"
          >
            {showMissing ? 'Hide' : 'View'}
          </Button>
          {showMissing && (
            <CaseListTable
              issues={issuesWithMissingChecks}
              fields={CHECKS_MISSING_TABLE_FIELDS}
            />
          )}
        </>
      )}
    </Alert>
  )
}

mount(App)
