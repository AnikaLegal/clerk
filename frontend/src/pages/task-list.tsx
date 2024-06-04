import React, { useState, useEffect } from 'react'
import {
  Container,
  Dropdown,
  Form,
  Header,
  Table,
  Input,
  Label,
} from 'semantic-ui-react'

import { mount, debounce } from 'utils'
import api from 'api'

import { FadeTransition } from 'comps/transitions'

interface DjangoContext {
  choices: {
    is_open: string[][]
    type: string[][]
    case_topic: string[][]
  }
}
const CONTEXT = (window as any).REACT_CONTEXT as DjangoContext
const debouncer = debounce(300)

const App = () => {
  const [isLoading, setIsLoading] = useState(false)
  const [tasks, setTasks] = useState<[]>([])
  const [query, setQuery] = useState<{}>({isOpen: "true"})
  const [getTasks] = api.useLazyGetTasksQuery()
  const [showAdvancedSearch, setShowAdvancedSearch] = useState(true)

  const search = debouncer(() => {
    setIsLoading(true)
    getTasks(query)
      .unwrap()
      .then((tasks) => {
        setTasks(tasks)
        setIsLoading(false)
      })
      .catch(() => setIsLoading(false))
  })
  useEffect(() => search(), [query])

  const updateQuery = (name, value) => {
    if (value === null || value === '') {
      const { [name]: tmp, ...rest } = query
      setQuery(rest)
    }
    else {
      setQuery({ ...query, [name]: value })
    }
  }

  return (
    <Container>
      <Header as="h1">Tasks</Header>
      <Form>
        <Form.Field>
          <Input
            placeholder="Search by file ref, task name, owner or assignee"
            value={query.q || ''}
            onChange={(e) => updateQuery('q', e.target.value)}
            loading={isLoading}
          />
        </Form.Field>
        {!showAdvancedSearch && (
          <Label
            style={{ cursor: 'pointer' }}
            onClick={(e) => {
              e.preventDefault()
              setShowAdvancedSearch(true)
            }}
          >
            Advanced search
          </Label>
        )}
        {showAdvancedSearch && (
          <>
            <Label
              style={{ cursor: 'pointer' }}
              onClick={(e) => {
                e.preventDefault()
                setShowAdvancedSearch(false)
              }}
            >
              Hide advanced search
            </Label>
            <Form.Group style={{ marginTop: '1em' }}>
              <Form.Field width={8}>
                <Dropdown
                  fluid
                  selection
                  clearable
                  value={query.isOpen || ''}
                  placeholder="Is task open?"
                  options={choiceToOptions(CONTEXT.choices.is_open)}
                  onChange={(e, { value }) => updateQuery('isOpen', value)}
                />
              </Form.Field>
              <Form.Field width={8}>
                <Dropdown
                  fluid
                  selection
                  clearable
                  value={query.issueTopic || ''}
                  placeholder="Case Topic"
                  options={choiceToOptions(CONTEXT.choices.case_topic)}
                  onChange={(e, { value }) => updateQuery('issueTopic', value)}
                />
              </Form.Field>
              <Form.Field width={8}>
                <Dropdown
                  fluid
                  selection
                  clearable
                  value={query.type || ''}
                  placeholder="Task Type"
                  options={choiceToOptions(CONTEXT.choices.type)}
                  onChange={(e, { value }) => updateQuery('type', value)}
                />
              </Form.Field>
            </Form.Group>
          </>
        )}
      </Form>
      <FadeTransition in={!isLoading}>
        <Table celled>
          <Table.Header>
            <Table.Row>
              <Table.HeaderCell>Fileref</Table.HeaderCell>
              <Table.HeaderCell>Topic</Table.HeaderCell>
              <Table.HeaderCell>Task Name</Table.HeaderCell>
              <Table.HeaderCell>Task Type</Table.HeaderCell>
              <Table.HeaderCell>Assigned To</Table.HeaderCell>
              <Table.HeaderCell>Owner</Table.HeaderCell>
              <Table.HeaderCell>Task Status</Table.HeaderCell>
            </Table.Row>
          </Table.Header>
          <Table.Body>
            {tasks.length < 1 && (
              <Table.Row>
                <td>No tasks found</td>
              </Table.Row>
            )}
            {tasks.map((task) => (
              <Table.Row key={task.id}>
                <Table.Cell>
                  <a href={task.issue.url}>{task.issue.fileref}</a>
                </Table.Cell>
                <Table.Cell>{task.issue.topic_display}</Table.Cell>
                <Table.Cell>
                  <a href={task.url}>{task.name}</a>
                </Table.Cell>
                <Table.Cell>{task.type.display}</Table.Cell>
                <Table.Cell>
                  <a href={task.assigned_to.url}>{task.assigned_to.full_name}</a>
                </Table.Cell>
                <Table.Cell>
                  <a href={task.owner.url}>{task.owner.full_name}</a>
                </Table.Cell>
                <Table.Cell>{task.status.display}</Table.Cell>
              </Table.Row>
            ))}
          </Table.Body>
        </Table>
      </FadeTransition>
    </Container>
  )
}

const choiceToOptions = (choices) =>
  choices.map(([value, label]) => ({
    key: label,
    text: label,
    value: value,
  }))

mount(App)
