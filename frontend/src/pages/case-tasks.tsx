import api from 'api'
import { CASE_TABS, CaseHeader, CaseTabUrls } from 'comps/case-header'
import React from 'react'
import { Container, Segment } from 'semantic-ui-react'
import { CaseFormServiceChoices } from 'types/case'
import { mount } from 'utils'

interface DjangoContext {
  case_pk: string
  choices: any
  urls: CaseTabUrls
}
const CONTEXT = (window as any).REACT_CONTEXT as DjangoContext

const App = () => {
  const caseId = CONTEXT.case_pk
  const urls = CONTEXT.urls

  const caseResult = api.useGetCaseQuery({ id: caseId })
  if (caseResult.isFetching) return null

  const issue = caseResult.data!.issue
  return (
    <Container>
      <CaseHeader issue={issue} activeTab={CASE_TABS.TASKS} urls={urls} />
    </Container>
  )
}

mount(App)
