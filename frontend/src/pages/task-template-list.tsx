import React, { useState } from 'react'
import { Button, Container, Header, Table } from 'semantic-ui-react'
import { useSnackbar } from 'notistack'

import { mount, choiceToMap } from 'utils'
import { FadeTransition } from 'comps/transitions'
import { useGetTaskTriggersQuery } from 'api'

interface DjangoContext {
  create_url: string
  choices: {
    topic: string[][]
    event: string[][]
    event_stage: string[][]
    tasks_assignment_role: string[][]
  }
}

const CONTEXT = (window as any).REACT_CONTEXT as DjangoContext
const TOPIC_LABELS = choiceToMap(CONTEXT.choices.topic)
const EVENT_LABELS = choiceToMap(CONTEXT.choices.event)
const EVENT_STAGE_LABELS = choiceToMap(CONTEXT.choices.event_stage)
const ROLES_LABELS = choiceToMap(CONTEXT.choices.tasks_assignment_role)

const App = () => {
  const { enqueueSnackbar } = useSnackbar()
  const taskTriggerResult = useGetTaskTriggersQuery()
  const taskTriggers = taskTriggerResult.data || []

  return (
    <Container>
      <Header as="h1">Task Templates</Header>
      <a href={CONTEXT.create_url}>
        <Button primary>Create a new task template</Button>
      </a>
      <FadeTransition in={!taskTriggerResult.isLoading}>
        <Table celled style={{ marginTop: '1rem' }}>
          <Table.Header>
            <Table.Row>
              <Table.HeaderCell>Name</Table.HeaderCell>
              <Table.HeaderCell>Topic</Table.HeaderCell>
              <Table.HeaderCell>Event</Table.HeaderCell>
              <Table.HeaderCell>Event Stage</Table.HeaderCell>
              <Table.HeaderCell>Assignment Role</Table.HeaderCell>
              <Table.HeaderCell>Date Created</Table.HeaderCell>
            </Table.Row>
          </Table.Header>
          <Table.Body>
            {taskTriggers.length < 1 && (
              <Table.Row>
                <td>No templates found</td>
              </Table.Row>
            )}
            {taskTriggers.map((t) => (
              <Table.Row key={t.id}>
                <Table.Cell>
                  <a href={t.url}>{t.name}</a>
                </Table.Cell>
                <Table.Cell>{TOPIC_LABELS.get(t.topic)}</Table.Cell>
                <Table.Cell>{EVENT_LABELS.get(t.event)}</Table.Cell>
                <Table.Cell>{EVENT_STAGE_LABELS.get(t.event_stage)}</Table.Cell>
                <Table.Cell>{ROLES_LABELS.get(t.tasks_assignment_role)}</Table.Cell>
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