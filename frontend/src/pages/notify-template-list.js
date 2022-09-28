import React, { useState } from 'react'
import {
  Button,
  Container,
  Header,
  Table,
  Input,
  Dropdown,
} from 'semantic-ui-react'

import { mount, debounce, useEffectLazy } from 'utils'
import { api } from 'api'
import { FadeTransition } from 'comps/transitions'

const CONTEXT = window.REACT_CONTEXT
const TOPIC_OPTIONS = [
  { key: 'GENERAL', value: 'GENERAL', text: 'General' },
  { key: 'REPAIRS', value: 'REPAIRS', text: 'Repairs' },
  { key: 'BONDS', value: 'BONDS', text: 'Bonds' },
  { key: 'EVICTION', value: 'EVICTION', text: 'Eviction' },
]

const debouncer = debounce(300)

const App = () => {
  const [isLoading, setIsLoading] = useState(false)
  const [notifications, setNotifications] = useState(CONTEXT.notifications)
  const [name, setName] = useState('')
  const [topic, setTopic] = useState('')
  const search = debouncer(() => {
    setIsLoading(true)
    api.templates.email
      .search({ name, topic })
      .then(({ data }) => {
        setNotifications(data)
        setIsLoading(false)
      })
      .catch(() => setIsLoading(false))
  })
  useEffectLazy(() => search(), [name, topic])
  return (
    <Container>
      <Header as="h1">Notification Templates</Header>
      <a href={CONTEXT.create_url}>
        <Button primary>Create a new notification template</Button>
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
          options={TOPIC_OPTIONS}
          onChange={(e, { value }) => setTopic(value)}
          value={topic}
        />
      </div>
      <FadeTransition in={!isLoading}>
        <Table celled>
          <Table.Header>
            <Table.Row>
              <Table.HeaderCell>Name</Table.HeaderCell>
              <Table.HeaderCell>Topic</Table.HeaderCell>
              <Table.HeaderCell>Event</Table.HeaderCell>
              <Table.HeaderCell>Channel</Table.HeaderCell>
              <Table.HeaderCell>Target</Table.HeaderCell>
              <Table.HeaderCell>Created At</Table.HeaderCell>
            </Table.Row>
          </Table.Header>
          <Table.Body>
            {notifications.length < 1 && (
              <Table.Row>
                <td>No notifications found</td>
              </Table.Row>
            )}
            {notifications.map((t) => (
              <Table.Row key={t.url}>
                <Table.Cell>
                  <a href={t.url}>{t.name}</a>
                </Table.Cell>
                <Table.Cell>{t.topic}</Table.Cell>
                <Table.Cell>{t.event}</Table.Cell>
                <Table.Cell>{t.channel}</Table.Cell>
                <Table.Cell>{t.target}</Table.Cell>
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
