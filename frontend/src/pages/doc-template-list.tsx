import React, { useState, useEffect } from 'react'
import {
  Button,
  Container,
  Header,
  Table,
  Input,
  Dropdown,
} from 'semantic-ui-react'
import { useSnackbar } from 'notistack'

import { mount, debounce, getAPIErrorMessage } from 'utils'
import { FadeTransition } from 'comps/transitions'
import api, { useDeleteDocumentTemplateMutation, DocumentTemplate } from 'api'

interface DjangoContext {
  topic_options: { key: string; value: string; text: string }[]
  topic: string
  create_url: string
}

const CONTEXT = (window as any).REACT_CONTEXT as DjangoContext

const debouncer = debounce(300)

const App = () => {
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const [templates, setTemplates] = useState<DocumentTemplate[]>([])
  const [name, setName] = useState('')
  const [topic, setTopic] = useState(CONTEXT.topic)
  const [searchTemplates] = api.useLazyGetDocumentTemplatesQuery()
  const [deleteDocumentTemplate] = useDeleteDocumentTemplateMutation()

  const { enqueueSnackbar } = useSnackbar()

  const onDelete = (id) => () => {
    const template = templates.filter((t) => t.id === id).pop()
    if (template && window.confirm(`Delete file ${template.name}?`)) {
      deleteDocumentTemplate({ id })
        .unwrap()
        .then(() => {
          setTemplates(templates.filter((t) => t.id !== id))
        })
        .catch((err) => {
          enqueueSnackbar(
            getAPIErrorMessage(err, 'Failed to delete this document template'),
            {
              variant: 'error',
            }
          )
        })
    }
  }
  const search = debouncer(() => {
    setIsLoading(true)
    searchTemplates({ name, topic })
      .unwrap()
      .then((templates) => {
        setTemplates(templates)
        setIsLoading(false)
      })
      .catch((err) => {
        enqueueSnackbar(getAPIErrorMessage(err, 'Failed to search templates'), {
          variant: 'error',
        })
        setIsLoading(false)
      })
  })
  useEffect(() => search(), [name, topic])
  return (
    <Container>
      <Header as="h1">Document Templates</Header>
      <a href={CONTEXT.create_url}>
        <Button primary>Upload document template</Button>
      </a>
      <div
        style={{
          margin: '1rem 0',
          display: 'grid',
          gap: '1rem',
          gridTemplateColumns: '1fr 1fr',
        }}
      >
        <Input
          icon="search"
          placeholder="Search by template name or subject..."
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
        <Dropdown
          fluid
          selection
          placeholder="Select a case type"
          options={CONTEXT.topic_options}
          onChange={(e, { value }) => setTopic(value as string)}
          value={topic}
        />
      </div>
      <FadeTransition in={!isLoading}>
        <Table celled>
          <Table.Header>
            <Table.Row>
              <Table.HeaderCell>Name</Table.HeaderCell>
              <Table.HeaderCell>Topic</Table.HeaderCell>
              <Table.HeaderCell>Created At</Table.HeaderCell>
              <Table.HeaderCell>Modified At</Table.HeaderCell>
              <Table.HeaderCell>Actions</Table.HeaderCell>
            </Table.Row>
          </Table.Header>
          <Table.Body>
            {templates.length < 1 && (
              <Table.Row>
                <td>No templates found</td>
              </Table.Row>
            )}
            {templates.map((t) => (
              <Table.Row key={t.url}>
                <Table.Cell>
                  <a href={t.url}>{t.name}</a>
                </Table.Cell>
                <Table.Cell>{t.topic}</Table.Cell>
                <Table.Cell>{t.created_at}</Table.Cell>
                <Table.Cell>{t.modified_at}</Table.Cell>
                <Table.Cell>
                  <Button negative basic onClick={onDelete(t.id)}>
                    Delete
                  </Button>
                </Table.Cell>
              </Table.Row>
            ))}
          </Table.Body>
        </Table>
      </FadeTransition>
    </Container>
  )
}

mount(App)
