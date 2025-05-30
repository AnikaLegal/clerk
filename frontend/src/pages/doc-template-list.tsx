import { Box, LoadingOverlay } from '@mantine/core'
import { useDebouncedCallback } from '@mantine/hooks'
import {
  GetDocumentTemplatesApiArg,
  useDeleteDocumentTemplateMutation,
  useGetDocumentTemplatesQuery,
} from 'api'
import { enqueueSnackbar } from 'notistack'
import React, { useState } from 'react'
import {
  Button,
  Container,
  Dropdown,
  Header,
  Input,
  Table,
} from 'semantic-ui-react'
import { choiceToMap, choiceToOptions, getAPIErrorMessage, mount } from 'utils'

import '@mantine/core/styles.css'

interface DjangoContext {
  choices: {
    topic: [string, string][]
  }
  create_url: string
}

const CONTEXT = (window as any).REACT_CONTEXT as DjangoContext
const TopicLabels = choiceToMap(CONTEXT.choices.topic)
const CreateUrl = CONTEXT.create_url

const App = () => {
  const [args, setArgs] = useState<GetDocumentTemplatesApiArg>({})
  const [deleteDocumentTemplate] = useDeleteDocumentTemplateMutation()

  const result = useGetDocumentTemplatesQuery(args)
  const data = result.data || []

  const onDelete = (id: number, name: string) => () => {
    if (window.confirm(`Delete file ${name}?`)) {
      deleteDocumentTemplate({ id })
        .unwrap()
        .then(() => {
          enqueueSnackbar('Document template deleted', { variant: 'success' })
        })
        .catch((e) => {
          enqueueSnackbar(
            getAPIErrorMessage(e, 'Failed to delete document template'),
            {
              variant: 'error',
            }
          )
        })
    }
  }

  const setArgByName = (
    name: keyof GetDocumentTemplatesApiArg,
    value: string
  ) => {
    setArgs((prev) => {
      return { ...prev, [name]: value }
    })
  }

  const onSearchChange = useDebouncedCallback(
    (event: React.ChangeEvent<HTMLInputElement>, { value }) => {
      setArgByName('name', value)
    },
    300
  )

  return (
    <Container>
      <Header as="h1">Document Templates</Header>
      <a href={CreateUrl}>
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
          placeholder="Search by template name..."
          onChange={onSearchChange}
        />
        <Dropdown
          fluid
          selection
          clearable
          placeholder="Select a case type"
          options={choiceToOptions(CONTEXT.choices.topic)}
          onChange={(e, { value }) => setArgByName('topic', value as string)}
        />
      </div>
      <Box pos="relative">
        <LoadingOverlay
          visible={result.isLoading}
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
            {!result.isLoading &&
              (data.length < 1 ? (
                <Table.Row>
                  <td>No templates found</td>
                </Table.Row>
              ) : (
                data.map((t) => (
                  <Table.Row key={t.url}>
                    <Table.Cell>
                      <a href={t.url}>{t.name}</a>
                    </Table.Cell>
                    <Table.Cell>{TopicLabels.get(t.topic)}</Table.Cell>
                    <Table.Cell>{t.created_at}</Table.Cell>
                    <Table.Cell>{t.modified_at}</Table.Cell>
                    <Table.Cell>
                      <Button negative basic onClick={onDelete(t.id, t.name)}>
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
