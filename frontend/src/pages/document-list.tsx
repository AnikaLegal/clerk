import React from 'react'
import { Container, Header, Loader } from 'semantic-ui-react'

import { useGetCaseDocumentsQuery, useGetCaseQuery } from 'api'
import { CASE_TABS, CaseHeader, CaseTabUrls } from 'comps/case-header'
import { mount } from 'utils'

interface DjangoContext {
  case_pk: string
  urls: CaseTabUrls
}

const { case_pk, urls } = (window as any).REACT_CONTEXT as DjangoContext

const Documents = ({
  result,
}: {
  result: ReturnType<typeof useGetCaseDocumentsQuery>
}) => {
  if (result.isFetching) {
    return (
      <Loader active inline="centered">
        Loading documents
      </Loader>
    )
  }
  if (result.isError) {
    return (
      <p>Could not load the case documents. Reload the page to try again.</p>
    )
  }
  const data = result.data
  if (!data?.sharepoint_url) {
    return (
      <p>
        This case has not been set up in SharePoint, which could be due to an
        error, contact the Anika tech team for help.
      </p>
    )
  }
  return (
    <>
      <p>
        View case documents in <a href={data.sharepoint_url}>SharePoint</a>.
      </p>
      {data.documents.map(({ name, url }) => (
        <li key={url}>
          <a href={url}>{name}</a>
        </li>
      ))}
    </>
  )
}

const App = () => {
  const caseResult = useGetCaseQuery({ id: case_pk })
  const docsResult = useGetCaseDocumentsQuery({ id: case_pk })

  if (caseResult.isLoading) {
    return null
  }
  if (caseResult.isError) {
    throw caseResult.error
  }
  if (!caseResult.isSuccess) {
    throw new Error('Unexpected query state')
  }

  return (
    <Container>
      <CaseHeader
        issue={caseResult.data.issue}
        activeTab={CASE_TABS.DOCUMENTS}
        urls={urls}
      />
      <Header as="h1">Documents</Header>
      <Documents result={docsResult} />
    </Container>
  )
}

mount(App)
