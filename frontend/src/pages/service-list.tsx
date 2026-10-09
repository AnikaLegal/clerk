import { Container } from '@mantine/core'
import api from 'api'
import { CASE_TABS, CaseHeader, CaseTabUrls } from 'comps/case-header'
import { ServiceSection } from 'features/service'
import React from 'react'
import { UserPermission } from 'types'
import { mount } from 'utils'

interface DjangoContext {
  case_pk: string
  urls: CaseTabUrls
  user: UserPermission
}
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const CONTEXT = (window as any).REACT_CONTEXT as DjangoContext

const App = () => {
  const caseId = CONTEXT.case_pk
  const urls = CONTEXT.urls
  const user = CONTEXT.user

  const caseResult = api.useGetCaseQuery({ id: caseId })
  if (caseResult.isFetching || !caseResult.data) {
    return null
  }
  const issue = caseResult.data.issue
  const canChange = issue.is_open || user.is_coordinator_or_better

  return (
    <Container size="xl">
      <CaseHeader issue={issue} activeTab={CASE_TABS.SERVICES} urls={urls} />
      <ServiceSection issue={issue} category="DISCRETE" canChange={canChange} />
      <ServiceSection issue={issue} category="ONGOING" canChange={canChange} />
    </Container>
  )
}

mount(App)
