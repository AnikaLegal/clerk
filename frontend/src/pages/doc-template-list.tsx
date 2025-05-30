import { enqueueSnackbar } from 'notistack'
import React, { useEffect, useState } from 'react'
import {
  Button,
  Container,
  Dropdown,
  Header,
  Input,
  Table,
} from 'semantic-ui-react'
import { LoadingOverlay, Box } from '@mantine/core'
import api, { DocumentTemplate, useDeleteDocumentTemplateMutation } from 'api'
import {
  choiceToMap,
  choiceToOptions,
  debounce,
  getAPIErrorMessage,
  mount,
} from 'utils'

import '@mantine/core/styles.css'

interface DjangoContext {
  choices: {
    topic: [string, string][]
  }
  create_url: string
}

const CONTEXT = (window as any).REACT_CONTEXT as DjangoContext

const debouncer = debounce(300)

const App = () => {
  const [isLoading, setIsLoading] = useState(true)
  const [templates, setTemplates] = useState<DocumentTemplate[]>([])
  const [name, setName] = useState('')
  const [topic, setTopic] = useState('')
  const [searchTemplates] = api.useLazyGetDocumentTemplatesQuery()
  const [deleteDocumentTemplate] = useDeleteDocumentTemplateMutation()

  const topicLabels = choiceToMap(CONTEXT.choices.topic)

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
      })
      .catch((err) => {
        enqueueSnackbar(getAPIErrorMessage(err, 'Failed to search templates'), {
          variant: 'error',
        })
      })
      .finally(() => {
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
          clearable
          placeholder="Select a case type"
          options={choiceToOptions(CONTEXT.choices.topic)}
          onChange={(e, { value }) => setTopic(value as string)}
          value={topic}
        />
      </div>
      <Box pos="relative">
        <LoadingOverlay
          visible={isLoading}
          overlayProps={{ radius: 'sm', blur: 2 }}
        />
        <Table celled>
          <Table.Header>
            <Table.Row>
              <Table.HeaderCell>Name</Table.HeaderCell>
              <Table.HeaderCell>Topic</Table.HeaderCell>
              <Table.HeaderCell>Created</Table.HeaderCell>
              <Table.HeaderCell>Modified</Table.HeaderCell>
              <Table.HeaderCell>Actions</Table.HeaderCell>
            </Table.Row>
          </Table.Header>
          <Table.Body>
            {!isLoading &&
              (templates.length < 1 ? (
                <Table.Row>
                  <td>No templates found</td>
                </Table.Row>
              ) : (
                templates.map((t) => (
                  <Table.Row key={t.url}>
                    <Table.Cell>
                      <a href={t.url}>{t.name}</a>
                    </Table.Cell>
                    <Table.Cell>{topicLabels.get(t.topic)}</Table.Cell>
                    <Table.Cell>{t.created_at}</Table.Cell>
                    <Table.Cell>{t.modified_at}</Table.Cell>
                    <Table.Cell>
                      <Button negative basic onClick={onDelete(t.id)}>
                        Delete
                      </Button>
                    </Table.Cell>
                  </Table.Row>
                ))
              ))}
          </Table.Body>
        </Table>
      </Box>
    </Container>
  )
}

mount(App)
