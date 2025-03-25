import { Task, TaskRequest, useGetTaskQuery } from 'api'
import { TASK_STATUSES } from 'consts'
import moment from 'moment'
import React from 'react'
import { Card, Grid, Header, Loader, Segment } from 'semantic-ui-react'
import { getTaskApprovalText } from './task-approval-table-cell'
import { TaskAssignedToNode } from './task-assigned-to-node'
import { ErrorMessage } from 'comps/error-message'

interface TaskInformationCardProps {
  task: Task
}

export const TaskInformationCard = ({ task }: TaskInformationCardProps) => {
  return (
    <Card fluid>
      <Card.Content header="Task information" />
      <Card.Content>
        <Grid>
          <Grid.Row columns={2}>
            <Grid.Column>
              <Header sub>Assigned to</Header>
              <TaskAssignedToNode task={task} />
            </Grid.Column>
            <Grid.Column>
              <Header sub>Status</Header>
              {TASK_STATUSES[task.status]}
            </Grid.Column>
          </Grid.Row>
          <Grid.Row columns={2}>
            <Grid.Column>
              <Header sub>Date created</Header>
              {moment(task.created_at).format('DD/MM/YYYY')}
            </Grid.Column>
            <Grid.Column>
              <Header sub>Date due</Header>
              {task.due_at || '-'}
            </Grid.Column>
          </Grid.Row>
          <Grid.Row columns={2}>
            <Grid.Column>
              <Header sub>Date closed</Header>
              {task.closed_at
                ? moment(task.closed_at).format('DD/MM/YYYY')
                : '-'}
            </Grid.Column>
            <Grid.Column>
              <Header sub>Days open</Header>
              {task.days_open}
            </Grid.Column>
          </Grid.Row>
        </Grid>
      </Card.Content>
      {task.request && task.type == 'APPROVAL' && (
        <Card.Content>
          <RequestingTaskInformation request={task.request} />
        </Card.Content>
      )}
    </Card>
  )
}

interface TaskRequestFromProps {
  request: TaskRequest
}

const RequestingTaskInformation = ({ request }: TaskRequestFromProps) => {
  const result = useGetTaskQuery({
    id: request.from_task_id,
  })
  if (result.isLoading) {
    return (
      <Segment basic>
        <Loader active />
      </Segment>
    )
  }
  if (result.isError) {
    return <ErrorMessage error={result.error} />
  }
  if (!result.data) {
    return null
  }

  const text = getTaskApprovalText(result.data)
  return (
    <Grid>
      <Grid.Row columns={1}>
        <Grid.Column>
          <Header sub>Requesting task</Header>
          <a href={result.data.url}>{result.data.name}</a>
        </Grid.Column>
      </Grid.Row>
      <Grid.Row columns={2}>
        <Grid.Column>
          <Header sub>Assigned to</Header>
          <TaskAssignedToNode task={result.data} />
        </Grid.Column>
        <Grid.Column>
          <Header sub>Approval?</Header>
          {text}
        </Grid.Column>
      </Grid.Row>
    </Grid>
  )
}
