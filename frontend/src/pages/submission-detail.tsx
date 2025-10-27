import {
  Box,
  Center,
  Container,
  Group,
  SegmentedControl,
  Title,
} from '@mantine/core'
import api from 'api'
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
      <Box m="lg">
        <Group justify="space-between">
          <Title order={2}>Original submission</Title>
          <SegmentedControl
            data={['Structured', 'Raw']}
            onChange={(value) => setShowRawAnswers(value === 'Raw')}
            disabled={!issue.submission_id}
          />
        </Group>
        <Box mt="lg">
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
        </Box>
      </Box>
    </Container>
  )
}

mount(App)
