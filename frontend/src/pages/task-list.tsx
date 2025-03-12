import api, { GetTasksApiArg, TaskList } from 'api'
import { TaskDueDateTableCell } from 'comps/task'
import { TaskApprovalTableCell } from 'comps/task/task-approval-table-cell'
import { FadeTransition } from 'comps/transitions'
import { CASE_TOPICS, TASK_IS_OPEN, TASK_STATUSES, TASK_TYPES } from 'consts'
import moment from 'moment'
import React, { useEffect, useState } from 'react'
import {
  Container,
  Dropdown,
  Form,
  Header,
  Icon,
  Input,
  Label,
  Table,
} from 'semantic-ui-react'
import { UserInfo } from 'types/global'
import { mount, useDebounce } from 'utils'

interface DjangoContext {
  user: UserInfo
}
const CONTEXT = (window as any).REACT_CONTEXT as DjangoContext

const App = () => {
  const [isLoading, setIsLoading] = useState(false)
  const [tasks, setTasks] = useState<TaskList[]>([])
  const [query, setQuery] = useState<string>()
  const [filter, setFilter] = useState<GetTasksApiArg>({
    isOpen: 'true',
    assignedTo: CONTEXT.user.id,
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
              <Form.Field>
                <Dropdown
                  fluid
                  selection
                  clearable
                  value={filter.isOpen || ''}
                  placeholder="Is task open?"
                  options={Object.entries(TASK_IS_OPEN).map(([key, value]) => ({
                    key: key,
                    value: key,
                    text: value,
                  }))}
                  onChange={(e, { value }) => updateFilter('isOpen', value)}
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
            <Form.Group widths="equal">
              <Form.Field>
                <Dropdown
                  fluid
                  selection
                  clearable
                  value={filter.issueTopic || ''}
                  placeholder="Case topic"
                  options={Object.entries(CASE_TOPICS).map(([key, value]) => ({
                    key: key,
                    value: key,
                    text: value,
                  }))}
                  onChange={(e, { value }) => updateFilter('issueTopic', value)}
                />
              </Form.Field>
              <Form.Field>
                <Dropdown
                  fluid
                  selection
                  clearable
                  value={filter.type || ''}
                  placeholder="Task type"
                  options={Object.entries(TASK_TYPES)
                    .map(([key, value]) => ({
                      key: key,
                      value: key,
                      text: value,
                    }))
                    .sort((a, b) => a.text.localeCompare(b.text))}
                  onChange={(e, { value }) => updateFilter('type', value)}
                />
              </Form.Field>
              <Form.Field>
                <Dropdown
                  fluid
                  selection
                  clearable
                  value={filter.status || ''}
                  placeholder="Task status"
                  options={Object.entries(TASK_STATUSES).map(
                    ([key, value]) => ({
                      key: key,
                      value: key,
                      text: value,
                    })
                  )}
                  onChange={(e, { value }) => updateFilter('status', value)}
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
              <Table.HeaderCell colSpan={2} textAlign="center">
                Case
              </Table.HeaderCell>
              <Table.HeaderCell colSpan={7} textAlign="center">
                Task
              </Table.HeaderCell>
            </Table.Row>
            <Table.Row>
              <Table.HeaderCell>Fileref</Table.HeaderCell>
              <Table.HeaderCell>Topic</Table.HeaderCell>
              <Table.HeaderCell>Name</Table.HeaderCell>
              <Table.HeaderCell>Type</Table.HeaderCell>
              <Table.HeaderCell>Assigned to</Table.HeaderCell>
              <Table.HeaderCell>Status</Table.HeaderCell>
              <Table.HeaderCell>Approval?</Table.HeaderCell>
              <Table.HeaderCell>Open?</Table.HeaderCell>
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
                <Table.Cell>{CASE_TOPICS[task.issue.topic]}</Table.Cell>
                <Table.Cell>
                  <a href={task.url}>{task.name}</a>
                </Table.Cell>
                <Table.Cell>{TASK_TYPES[task.type]}</Table.Cell>
                <Table.Cell>
                  {task.assigned_to && (
                    <a href={task.assigned_to.url}>
                      {task.assigned_to.full_name}
                    </a>
                  )}
                </Table.Cell>
                <Table.Cell>{TASK_STATUSES[task.status]}</Table.Cell>
                <TaskApprovalTableCell task={task} />
                <Table.Cell textAlign="center">
                  {task.is_open ? (
                    <Icon name="check" color="green" />
                  ) : (
                    <Icon name="close" color="yellow" />
                  )}
                </Table.Cell>
                <Table.Cell>
                  {moment(task.created_at).format('DD/MM/YYYY')}
                </Table.Cell>
                <TaskDueDateTableCell task={task} />
              </Table.Row>
            ))}
          </Table.Body>
        </Table>
      </FadeTransition>
    </Container>
  )
}
mount(App)
