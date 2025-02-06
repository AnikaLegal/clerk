import api, { Issue, TaskCreate } from 'api'
import { CASE_TABS, CaseHeader, CaseTabUrls } from 'comps/case-header'
import { FormikHelpers } from 'formik'
import React, { useState } from 'react'
import {
  Button,
  ButtonProps,
  Container,
  Grid,
  Header,
  Loader,
  Segment,
  Table,
} from 'semantic-ui-react'
import { mount, choiceToMap } from 'utils'
import moment from 'moment'

export interface CaseTasksChoices {
  status: string[][]
  type: string[][]
}

interface DjangoContext {
  case_pk: string
  choices: CaseTasksChoices
  urls: CaseTabUrls
}
const CONTEXT = (window as any).REACT_CONTEXT as DjangoContext
const TYPE_LABELS = choiceToMap(CONTEXT.choices.type)
const STATUS_LABELS = choiceToMap(CONTEXT.choices.status)

const App = () => {
  const caseId = CONTEXT.case_pk
  const urls = CONTEXT.urls

  const caseResult = api.useGetCaseQuery({ id: caseId })
  if (caseResult.isFetching) return null

  const issue = caseResult.data!.issue
  return (
    <Container>
      <CaseHeader issue={issue} activeTab={CASE_TABS.TASKS} urls={urls} />
      <Segment basic>
        <CaseTasks issue={issue} />
      </Segment>
    </Container>
  )
}

export interface CaseTasksProps {
  issue: Issue
}

export const CaseTasks = ({ issue }: CaseTasksProps) => {
  return (
    <>
      <Grid>
        <Grid.Row>
          <Grid.Column style={{ flexGrow: '1' }}>
            <Header as="h2">Case tasks</Header>
          </Grid.Column>
          {issue.is_open && (
            <Grid.Column style={{ width: 'auto' }}>
              <AddTaskButton floated="right" size="tiny" issue={issue}>
                Add task
              </AddTaskButton>
            </Grid.Column>
          )}
        </Grid.Row>
      </Grid>
      <CaseTasksTable issue={issue} />
    </>
  )
}

export interface AddTaskButtonProps {
  issue: Issue
  children: string | number
}

export const AddTaskButton = ({
  issue,
  children,
  ...props
}: AddTaskButtonProps & ButtonProps) => {
  const [open, setOpen] = useState(false)

  const handleSubmit = (
    values: TaskCreate,
    { setSubmitting, setErrors, resetForm }: FormikHelpers<TaskCreate>
  ) => {}

  return (
    <>
      <Button {...props} onClick={() => setOpen(true)}>
        {children}
      </Button>
    </>
  )
}

export interface CaseTasksTableProps {
  issue: Issue
}

export const CaseTasksTable = ({ issue }: CaseTasksTableProps) => {
  const result = api.useGetTasksQuery({
    issue: issue.id,
  })
  if (result.isLoading) {
    return <Loader active inline="centered" />
  }
  if (result.data.length == 0) {
    return (
      <Segment textAlign="center" secondary>
        <p>No tasks exist for this case.</p>
      </Segment>
    )
  }

  // TODO: handle unassigned tasks.
  // Beware of users with the same name but different ids.
  const tasksByUserName = Object.entries(
    Object.groupBy(result.data, ({ assigned_to }) => assigned_to?.id)
  ).map(([key, values]) => {
    return { name: values[0].assigned_to.full_name, tasks: values }
  })

  return (
    <Table celled structured>
      <Table.Header>
        <Table.Row>
          <Table.HeaderCell>Assigned To</Table.HeaderCell>
          <Table.HeaderCell>Task name</Table.HeaderCell>
          <Table.HeaderCell>Type</Table.HeaderCell>
          <Table.HeaderCell>Status</Table.HeaderCell>
          <Table.HeaderCell>Created</Table.HeaderCell>
          <Table.HeaderCell>Due date</Table.HeaderCell>
        </Table.Row>
      </Table.Header>
      <Table.Body>
        {tasksByUserName.map(({ name, tasks }) => (
          <>
            {tasks.map((task, index) => (
              <Table.Row>
                {index == 0 && (
                  <Table.Cell rowSpan={tasks.length}>{name}</Table.Cell>
                )}
                <Table.Cell>{task.name}</Table.Cell>
                <Table.Cell>{TYPE_LABELS.get(task.type)}</Table.Cell>
                <Table.Cell>{STATUS_LABELS.get(task.status)}</Table.Cell>
                <Table.Cell>
                  {moment(task.created_at).format('DD/MM/YYYY')}
                </Table.Cell>
                <Table.Cell>{task.due_at}</Table.Cell>
              </Table.Row>
            ))}
          </>
        ))}
      </Table.Body>
    </Table>
  )
}

mount(App)
