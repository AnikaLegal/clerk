import React, { useState, useEffect } from 'react'
import {
  Button,
  Container,
  Header,
  Table,
  Input,
  Loader,
  Dropdown,
  Label,
  Icon,
} from 'semantic-ui-react'

import { mount } from 'utils'
import { CaseHeader, CASE_TABS } from 'comps/case-header'
import { useGetCaseQuery, useGetCaseDocumentsQuery } from 'apiNew'

interface DjangoContext {
  case_pk: string
  urls: {
    detail: string
    email: string
    docs: string
  }
}

const { case_pk, urls } = (window as any).REACT_CONTEXT as DjangoContext

const App = () => {
  const caseResult = useGetCaseQuery({ id: case_pk })
  const docsResult = useGetCaseDocumentsQuery({ id: case_pk })

  const isInitialLoad = caseResult.isLoading
  const isLoading = caseResult.isFetching || docsResult.isFetching
  if (isInitialLoad) return null

  const sharepointUrl = docsResult.data?.sharepoint_url
  const documents = docsResult.data?.documents
  const issue = caseResult.data!.issue
  return (
    <Container>
      <CaseHeader issue={issue} activeTab={CASE_TABS.DOCUMENTS} urls={urls} />
      <Header as="h1">Documents</Header>
      {isLoading && (
        <Loader active inline="centered">
          Loading documents
        </Loader>
      )}
      {!isLoading && !sharepointUrl && (
        <p>
          This case has not been set up in SharePoint, which could be due to an
          error, contact the Anika tech team for help.
        </p>
      )}
      {!isLoading && sharepointUrl && (
        <p>
          View case documents in <a href={sharepointUrl}>SharePoint</a>.
        </p>
      )}
      {!isLoading &&
        documents.map(([name, url]) => (
          <li key={url}>
            <a href={url}>{name}</a>
          </li>
        ))}
    </Container>
  )
}

mount(App)
