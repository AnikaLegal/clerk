import { Box, LoadingOverlay } from '@mantine/core'
import { useDebouncedCallback } from '@mantine/hooks'
import {
  GetDocumentTemplatesApiArg,
  useDeleteDocumentTemplateMutation,
  useGetDocumentTemplatesQuery,
} from 'api'
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
            <DocumentTemplateTableBody result={result} onDelete={onDelete} />
          </Table.Body>
        </Table>
      </Box>
    </Container>
  )
}

const ErrorState = ({ error }: { error: any }) => {
  useEffect(() => {
    const message = getAPIErrorMessage(
      error,
      'Could not load document templates'
    )
    enqueueSnackbar(message, { variant: 'error' })
  }, [error])

  return (
    <Table.Row>
      <td colSpan={5}>Could not load document templates.</td>
    </Table.Row>
  )
}

const LoadingState = () => (
  <Table.Row>
    <td colSpan={5}>
      <LoadingOverlay visible overlayProps={{ radius: 'sm', blur: 30 }} />
    </td>
  </Table.Row>
)

const EmptyState = () => (
  <Table.Row>
    <td colSpan={5}>No templates found.</td>
  </Table.Row>
)

interface DocumentTemplateTableBodyProps {
  result: ReturnType<typeof useGetDocumentTemplatesQuery>
  onDelete: (id: number, name: string) => () => void
}

const DocumentTemplateTableBody = ({
  result,
  onDelete,
}: DocumentTemplateTableBodyProps) => {
  if (result.isError) {
    return <ErrorState error={result.error} />
  }
  if (result.isLoading) {
    return <LoadingState />
  }

  const data = result.data || []
  if (data.length < 1) {
    return <EmptyState />
  }

  return (
    <>
      {data.map((template) => (
        <Table.Row key={template.url}>
          <Table.Cell>
            <a href={template.url}>{template.name}</a>
          </Table.Cell>
          <Table.Cell>{TopicLabels.get(template.topic)}</Table.Cell>
          <Table.Cell>{template.created_at}</Table.Cell>
          <Table.Cell>{template.modified_at}</Table.Cell>
          <Table.Cell>
            <Button
              negative
              basic
              onClick={onDelete(template.id, template.name)}
            >
              Delete
            </Button>
          </Table.Cell>
        </Table.Row>
      ))}
    </>
  )
}

mount(App)
