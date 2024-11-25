import React, { useState } from 'react'
import {
  Button,
  Container,
  Header,
  Table,
  Input,
  Dropdown,
} from 'semantic-ui-react'
import { useSnackbar } from 'notistack'

import { mount, debounce, useEffectLazy, getAPIErrorMessage } from 'utils'
import { FadeTransition } from 'comps/transitions'
import api, { EmailTemplate } from 'api'

interface DjangoContext {
  topic_options: { key: string; value: string; text: string }[]
  templates: EmailTemplate[]
  create_url: string
}

const CONTEXT = (window as any).REACT_CONTEXT as DjangoContext

const debouncer = debounce(300)

const App = () => {
  const [isLoading, setIsLoading] = useState<boolean>(false)
  const [templates, setTemplates] = useState<EmailTemplate[]>(CONTEXT.templates)
  const [name, setName] = useState('')
  const [topic, setTopic] = useState('')
  const [searchTemplates] = api.useLazyGetEmailTemplatesQuery()
  const { enqueueSnackbar } = useSnackbar()
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
  useEffectLazy(() => search(), [name, topic])
  return (
    <Container>
      <Header as="h1">Email Templates</Header>
      <a href={CONTEXT.create_url}>
        <Button primary>Create a new email template</Button>
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
              <Table.HeaderCell>Subject</Table.HeaderCell>
              <Table.HeaderCell>Created</Table.HeaderCell>
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
                <Table.Cell>{t.subject}</Table.Cell>
                <Table.Cell>{t.created_at}</Table.Cell>
              </Table.Row>
            ))}
          </Table.Body>
        </Table>
      </FadeTransition>
    </Container>
  )
}

mount(App)
