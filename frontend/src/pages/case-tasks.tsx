import api, { Issue } from 'api'
import { CASE_TABS, CaseHeader, CaseTabUrls } from 'comps/case-header'
import { TaskApprovalTableCell, TaskDueDateTableCell } from 'comps/task'
import { CreateTaskModal } from 'comps/task/modal'
import moment from 'moment'
import React, { useState } from 'react'
import {
  Button,
  Container,
  Grid,
  Header,
  Icon,
  Loader,
  Segment,
  Table,
} from 'semantic-ui-react'
import { UserInfo } from 'types/global'
import { choiceToMap, mount } from 'utils'

export interface CaseTasksChoices {
  status: string[][]
}

interface DjangoContext {
  case_pk: string
  choices: CaseTasksChoices
  urls: CaseTabUrls
  user: UserInfo
}
const CONTEXT = (window as any).REACT_CONTEXT as DjangoContext
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
        <CaseTasks issue={issue} user={CONTEXT.user} />
      </Segment>
    </Container>
  )
}

export interface CaseTasksProps {
  issue: Issue
  user: UserInfo
}

export const CaseTasks = ({ issue, user }: CaseTasksProps) => {
  const [open, setOpen] = useState(false)

  return (
    <>
      <CreateTaskModal
        issue={issue}
        open={open}
        onClose={() => setOpen(false)}
        user={user}
      />
      <Grid>
        <Grid.Row>
          <Grid.Column style={{ flexGrow: '1' }}>
            <Header as="h2">Case tasks</Header>
          </Grid.Column>
          {issue.is_open && user.is_coordinator_or_better && (
            <Grid.Column style={{ width: 'auto' }}>
              <Button primary onClick={() => setOpen(true)}>
                Add a task
              </Button>
            </Grid.Column>
          )}
        </Grid.Row>
      </Grid>
      <CaseTasksTable issue={issue} />
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
  if (!result.data || result.data.length == 0) {
    return (
      <Segment textAlign="center" secondary>
        <p>No tasks exist for this case.</p>
      </Segment>
    )
  }

  return (
    <Table celled structured>
      <Table.Header>
        <Table.Row>
          <Table.HeaderCell>Name</Table.HeaderCell>
          <Table.HeaderCell>Type</Table.HeaderCell>
          <Table.HeaderCell>Assigned To</Table.HeaderCell>
          <Table.HeaderCell>Status</Table.HeaderCell>
          <Table.HeaderCell>Approval?</Table.HeaderCell>
          <Table.HeaderCell>Open?</Table.HeaderCell>
          <Table.HeaderCell>Created</Table.HeaderCell>
          <Table.HeaderCell>Due date</Table.HeaderCell>
        </Table.Row>
      </Table.Header>
      <Table.Body>
        {result.data.map((task) => (
          <Table.Row>
            <Table.Cell>
              <a href={task.url}>{task.name}</a>
            </Table.Cell>
            <Table.Cell>{task.type_display}</Table.Cell>
            <Table.Cell>
              {task.assigned_to && (
                <a href={task.assigned_to.url}>{task.assigned_to.full_name}</a>
              )}
            </Table.Cell>
            <Table.Cell>{STATUS_LABELS.get(task.status)}</Table.Cell>
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
  )
}

mount(App)
