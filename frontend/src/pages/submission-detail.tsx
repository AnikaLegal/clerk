import {
  Card,
  CardProps,
  Center,
  Container,
  Group,
  SegmentedControl,
  Table,
  Text,
  Title,
} from '@mantine/core'
import api, { BooleanYesNo, ChoiceDisplay, SubmissionAnswers } from 'api'
import { CASE_TABS, CaseHeader, CaseTabUrls } from 'comps/case-header'
import { EmptyState, SubmissionAnswersDisplay } from 'features/submission'
import React, { useState } from 'react'
import { mount } from 'utils'

interface DjangoContext {
  case_pk: string
  urls: CaseTabUrls
}
const CONTEXT = (window as any).REACT_CONTEXT as DjangoContext

const App = () => {
  const caseId = CONTEXT.case_pk
  const urls = CONTEXT.urls

  const [showRawAnswers, setShowRawAnswers] = useState(false)
  const result = api.useGetCaseQuery({ id: caseId })
  if (result.isFetching || !result.data) {
    return null
  }
  const issue = result.data.issue

  return (
    <Container size="xl">
      <CaseHeader issue={issue} activeTab={CASE_TABS.SUBMISSION} urls={urls} />
      <Card mt="md">
        <Card.Section>
          <Group justify="flex-end">
            <SegmentedControl
              data={['Structured', 'Raw']}
              onChange={(value) => setShowRawAnswers(value === 'Raw')}
              disabled={!issue.submission_id}
            />
          </Group>
        </Card.Section>
        <Card.Section>
          {issue.submission_id ? (
            <SubmissionAnswersDisplay
              submissionId={issue.submission_id}
              showRawAnswers={showRawAnswers}
            />
          ) : (
            <Center>
              <EmptyState />
            </Center>
          )}
        </Card.Section>
      </Card>
    </Container>
  )
}

mount(App)
