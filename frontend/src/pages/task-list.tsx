import api, { GetTasksApiArg, TaskList } from 'api'
import { FadeTransition } from 'comps/transitions'
import moment from 'moment'
import React, { useEffect, useState } from 'react'
import {
  Container,
  Dropdown,
  Form,
  Header,
  Input,
  Label,
  Table,
  SemanticCOLORS,
} from 'semantic-ui-react'
import { UserPermission } from 'types/global'
import { choiceToMap, choiceToOptions, mount, useDebounce } from 'utils'

interface DjangoContext {
  choices: {
    type: string[][]
    status: string[][]
    is_open: string[][]
    case_topic: string[][]
    my_tasks: string[][]
  }
  user: UserPermission
}

const CONTEXT = (window as any).REACT_CONTEXT as DjangoContext
const TOPIC_LABELS = choiceToMap(CONTEXT.choices.case_topic)
const TYPE_LABELS = choiceToMap(CONTEXT.choices.type)
const STATUS_LABELS = choiceToMap(CONTEXT.choices.status)

const App = () => {
  const [isLoading, setIsLoading] = useState(false)
  const [tasks, setTasks] = useState<TaskList[]>([])
  const [query, setQuery] = useState<string>()
  const [filter, setFilter] = useState<GetTasksApiArg>({
    isOpen: 'true',
    myTasks: 'true',
  })
  const [showAdvancedSearch, setShowAdvancedSearch] = useState(true)
  const [getTasks] = api.useLazyGetTasksQuery()

  const debouncedQuery = useDebounce(query, 300)

  const search = () => {
    setIsLoading(true)
    getTasks(filter)
      .unwrap()
      .then((tasks) => {
        setTasks(tasks)
        setIsLoading(false)
      })
      .catch(() => setIsLoading(false))
  }
  useEffect(() => search(), [filter])

  const updateFilter = (name: keyof GetTasksApiArg, value) => {
    var updated = {}
    if (value === null || value === '') {
      const { [name]: _, ...remaining } = filter
      updated = remaining
    } else {
      updated = { ...filter, [name]: value }
    }
    setFilter(updated)
  }

  const updateQuery = () => {
    updateFilter('q', debouncedQuery)
  }
  useEffect(() => updateQuery(), [debouncedQuery])

  const userResults = api.useGetUsersQuery({ isActive: true, sort: 'email' })
  const users = userResults.data ?? []

  const getDueDateColor = (task: TaskList): SemanticCOLORS => {
    if (task.is_urgent) {
      return 'red'
    }
    if (task.due_at) {
      const now = moment().startOf('day')
      const due_at = moment(task.due_at, 'DD/MM/YYYY')
      const days = due_at.diff(now, 'days')
      if (days <= 7) {
        if (days >= 3) {
          return 'green'
        } else if (days >= 2) {
          return 'yellow'
        } else if (days >= 1) {
          return 'orange'
        } else {
          return 'red'
        }
      }
    }
    return null
  }

  return (
    <Container>
      <Header as="h1">
        Tasks
        <Header.Subheader>Showing {tasks.length} tasks</Header.Subheader>
      </Header>
      <Form>
        <Form.Field>
          <Input
            placeholder="Search by file ref, task name or assignee"
            value={query || ''}
            onChange={(e) => setQuery(e.target.value)}
            loading={isLoading}
          />
        </Form.Field>
        <Label
          style={{ cursor: 'pointer', marginBottom: '1rem' }}
          onClick={(e) => {
            e.preventDefault()
            setShowAdvancedSearch(!showAdvancedSearch)
          }}
        >
          {showAdvancedSearch ? 'Hide advanced search' : 'Advanced search'}
        </Label>
        {showAdvancedSearch && (
          <>
            <Form.Group widths="equal">
              {CONTEXT.user.is_coordinator_or_better && (
                <Form.Field>
                  <Dropdown
                    clearable
                    fluid
                    search
                    selection
                    value={filter.myTasks || ''}
                    placeholder="My tasks?"
                    options={choiceToOptions(CONTEXT.choices.my_tasks)}
                    onChange={(e, { value }) => updateFilter('myTasks', value)}
                  />
                </Form.Field>
              )}
              <Form.Field>
                <Dropdown
                  fluid
                  selection
                  clearable
                  value={filter.isOpen || ''}
                  placeholder="Is task open?"
                  options={choiceToOptions(CONTEXT.choices.is_open)}
                  onChange={(e, { value }) => updateFilter('isOpen', value)}
                />
              </Form.Field>
              <Form.Field>
                <Dropdown
                  fluid
                  selection
                  clearable
                  value={filter.issueTopic || ''}
                  placeholder="Case Topic"
                  options={choiceToOptions(CONTEXT.choices.case_topic)}
                  onChange={(e, { value }) => updateFilter('issueTopic', value)}
                />
              </Form.Field>
            </Form.Group>
            <Form.Group widths="equal">
              <Form.Field>
                <Dropdown
                  fluid
                  selection
                  clearable
                  value={filter.type || ''}
                  placeholder="Task Type"
                  options={choiceToOptions(CONTEXT.choices.type)}
                  onChange={(e, { value }) => updateFilter('type', value)}
                />
              </Form.Field>
              <Form.Field>
                <Dropdown
                  fluid
                  selection
                  clearable
                  value={filter.status || ''}
                  placeholder="Task Status"
                  options={choiceToOptions(CONTEXT.choices.status)}
                  onChange={(e, { value }) => updateFilter('status', value)}
                />
              </Form.Field>
              <Form.Field>
                <Dropdown
                  clearable
                  fluid
                  search
                  selection
                  value={filter.assignedTo || ''}
                  placeholder="Assignee"
                  options={users.map((u) => ({
                    key: u.id,
                    value: u.id,
                    text: u.email,
                  }))}
                  onChange={(e, { value }) => updateFilter('assignedTo', value)}
                  loading={userResults.isLoading}
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
              <Table.HeaderCell>Task name</Table.HeaderCell>
              <Table.HeaderCell>Task type</Table.HeaderCell>
              <Table.HeaderCell>Assigned to</Table.HeaderCell>
              <Table.HeaderCell>Task status</Table.HeaderCell>
              <Table.HeaderCell>Created</Table.HeaderCell>
              <Table.HeaderCell>Due date</Table.HeaderCell>
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
                <Table.Cell>{TOPIC_LABELS.get(task.issue.topic)}</Table.Cell>
                <Table.Cell>
                  <a href={task.url}>{task.name}</a>
                </Table.Cell>
                <Table.Cell>{TYPE_LABELS.get(task.type)}</Table.Cell>
                <Table.Cell>
                  {task.assigned_to && (
                    <a href={task.assigned_to.url}>
                      {task.assigned_to.full_name}
                    </a>
                  )}
                </Table.Cell>
                <Table.Cell>{STATUS_LABELS.get(task.status)}</Table.Cell>
                <Table.Cell>{task.created_at}</Table.Cell>
                <Table.Cell
                  className={getDueDateColor(task)}
                  textAlign="center"
                >
                  {task.is_urgent ? (
                    <span className="animation-tada">URGENT</span>
                  ) : (
                    task.due_at || '-'
                  )}
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
