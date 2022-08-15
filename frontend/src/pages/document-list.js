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
import { api } from 'api'

const { issue, load_sharepoint_url, urls } = window.REACT_CONTEXT

const App = () => {
  const [isLoading, setIsLoading] = useState(true)
  const [sharepointInfo, setSharepointInfo] = useState({
    sharepointUrl: null,
    documents: [],
  })
  const { sharepointUrl, documents } = sharepointInfo
  useEffect(() => {
    api.case.docs(issue.id).then(({ resp, data }) => {
      if (resp.ok) {
        setSharepointInfo({
          sharepointUrl: data.sharepoint_url,
          documents: data.documents,
        })
      }
      setIsLoading(false)
    })
  }, [])
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
