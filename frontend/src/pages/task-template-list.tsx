import React from 'react'
import { Button, Container, Header, Table } from 'semantic-ui-react'

import { useGetTaskTriggersQuery } from 'api'
import { FadeTransition } from 'comps/transitions'
import {
  CASE_EVENT_TYPES,
  CASE_STAGES,
  TASK_TRIGGER_ROLES,
  TASK_TRIGGER_TOPICS,
} from 'consts'
import moment from 'moment'
import { mount } from 'utils'

interface DjangoContext {
  create_url: string
}

const CONTEXT = (window as any).REACT_CONTEXT as DjangoContext

const App = () => {
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
              <Table.HeaderCell>Event stage</Table.HeaderCell>
              <Table.HeaderCell>Assignment role</Table.HeaderCell>
              <Table.HeaderCell>Created</Table.HeaderCell>
            </Table.Row>
          </Table.Header>
          <Table.Body>
            {taskTriggers.length < 1 && (
              <Table.Row>
                <td>No templates found</td>
              </Table.Row>
            )}
            {taskTriggers.map((trigger) => (
              <Table.Row key={trigger.id}>
                <Table.Cell>
                  <a href={trigger.url}>{trigger.name}</a>
                </Table.Cell>
                <Table.Cell>{TASK_TRIGGER_TOPICS[trigger.topic]}</Table.Cell>
                <Table.Cell>{CASE_EVENT_TYPES[trigger.event]}</Table.Cell>
                <Table.Cell>
                  {trigger.event_stage ? CASE_STAGES[trigger.event_stage] : '-'}
                </Table.Cell>
                <Table.Cell>
                  {TASK_TRIGGER_ROLES[trigger.tasks_assignment_role]}
                </Table.Cell>
                <Table.Cell>
                  {moment(trigger.created_at).format('DD/MM/YYYY')}
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
