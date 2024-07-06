import React, { useState, useEffect } from "react"
import {
  Container,
  Dropdown,
  Form,
  Header,
  Table,
  Input,
  Label,
} from "semantic-ui-react"
import { mount, useDebounce, choiceToMap, choiceToOptions } from "utils"
import api from "api"
import { FadeTransition } from "comps/transitions"

interface DjangoContext {
  choices: {
    type: string[][]
    status: string[][]
    is_open: string[][]
    case_topic: string[][]
    my_tasks: string[][]
  }
}

const CONTEXT = (window as any).REACT_CONTEXT as DjangoContext
const TOPIC_LABELS = choiceToMap(CONTEXT.choices.case_topic)
const TYPE_LABELS = choiceToMap(CONTEXT.choices.type)
const STATUS_LABELS = choiceToMap(CONTEXT.choices.status)

const App = () => {
  const [isLoading, setIsLoading] = useState(false)
  const [tasks, setTasks] = useState<[]>([])
  const [query, setQuery] = useState<string>()
  const [filter, setFilter] = useState<{}>({ isOpen: "true", myTasks: "true" })
  const [showAdvancedSearch, setShowAdvancedSearch] = useState(true)
  const [getTasks] = api.useLazyGetTasksQuery()

  const debouncedQuery = useDebounce(query, 300);

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

  const updateFilter = (name, value) => {
    var updated = {}
    if (value === null || value === "") {
      const { [name]: _, ...remaining } = filter
      updated = remaining
    }
    else {
      updated = { ...filter, [name]: value }
    }
    setFilter(updated)
  }

  const updateQuery = () => {
    updateFilter("q", debouncedQuery)
  }
  useEffect(() => updateQuery(), [debouncedQuery])

  const userResults = api.useGetUsersQuery({isActive: true, sort: "email"})
  const users = userResults.data ?? []

  return (
    <Container>
      <Header as="h1">Tasks
        <Header.Subheader>
          Showing {tasks.length} tasks
        </Header.Subheader>
      </Header>
      <Form>
        <Form.Field>
          <Input
            placeholder="Search by file ref, task name, owner or assignee"
            value={query || ""}
            onChange={(e) => setQuery(e.target.value)}
            loading={isLoading}
          />
        </Form.Field>
        {!showAdvancedSearch && (
          <Label
            style={{ cursor: "pointer" }}
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
              style={{ cursor: "pointer" }}
              onClick={(e) => {
                e.preventDefault()
                setShowAdvancedSearch(false)
              }}
            >
              Hide advanced search
            </Label>
            <Form.Group style={{ marginTop: "1em" }}>
              <Form.Field width={8}>
                <Dropdown
                  clearable
                  fluid
                  search
                  selection
                  value={filter.myTasks || ""}
                  placeholder="My tasks?"
                  options={choiceToOptions(CONTEXT.choices.my_tasks)}
                  onChange={(e, { value }) => updateFilter("myTasks", value)}
                />
              </Form.Field>
              <Form.Field width={8}>
                <Dropdown
                  fluid
                  selection
                  clearable
                  value={filter.isOpen || ""}
                  placeholder="Is task open?"
                  options={choiceToOptions(CONTEXT.choices.is_open)}
                  onChange={(e, { value }) => updateFilter("isOpen", value)}
                />
              </Form.Field>
              <Form.Field width={8}>
                <Dropdown
                  fluid
                  selection
                  clearable
                  value={filter.issueTopic || ""}
                  placeholder="Case Topic"
                  options={choiceToOptions(CONTEXT.choices.case_topic)}
                  onChange={(e, { value }) => updateFilter("issueTopic", value)}
                />
              </Form.Field>
              <Form.Field width={8}>
                <Dropdown
                  fluid
                  selection
                  clearable
                  value={filter.type || ""}
                  placeholder="Task Type"
                  options={choiceToOptions(CONTEXT.choices.type)}
                  onChange={(e, { value }) => updateFilter("type", value)}
                />
              </Form.Field>
            </Form.Group>
            <Form.Group style={{ marginTop: "1em" }}>
              <Form.Field width={8}>
                <Dropdown
                  fluid
                  selection
                  clearable
                  value={filter.status || ""}
                  placeholder="Task Status"
                  options={choiceToOptions(CONTEXT.choices.status)}
                  onChange={(e, { value }) => updateFilter("status", value)}
                />
              </Form.Field>
              <Form.Field width={8}>
                <Dropdown
                  clearable
                  fluid
                  search
                  selection
                  value={filter.assignedTo || ""}
                  placeholder="Assignee"
                  options={users.map((u) => ({
                    key: u.id,
                    value: u.id,
                    text: u.email,
                  }))}
                  onChange={(e, { value }) => updateFilter("assignedTo", value)}
                  loading={userResults.isLoading}
                />
              </Form.Field>
              <Form.Field width={8}>
                <Dropdown
                  clearable
                  fluid
                  search
                  selection
                  value={filter.owner || ""}
                  placeholder="Owner"
                  options={users.map((u) => ({
                    key: u.id,
                    value: u.id,
                    text: u.email,
                  }))}
                  onChange={(e, { value }) => updateFilter("owner", value)}
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
              <Table.HeaderCell>Task Name</Table.HeaderCell>
              <Table.HeaderCell>Task Type</Table.HeaderCell>
              <Table.HeaderCell>Assigned To</Table.HeaderCell>
              <Table.HeaderCell>Owner</Table.HeaderCell>
              <Table.HeaderCell>Task Status</Table.HeaderCell>
              <Table.HeaderCell>Days Open</Table.HeaderCell>
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
                  <a href={task.assigned_to.url}>{task.assigned_to.full_name}</a>
                </Table.Cell>
                <Table.Cell>
                  <a href={task.owner.url}>{task.owner.full_name}</a>
                </Table.Cell>
                <Table.Cell>{STATUS_LABELS.get(task.status)}</Table.Cell>
                <Table.Cell>{task.days_open}</Table.Cell>
              </Table.Row>
            ))}
          </Table.Body>
        </Table>
      </FadeTransition>
    </Container>
  )
}
mount(App)
