import { Task, TaskRequest, useGetTaskQuery } from 'api'
import React from 'react'
import {
  Card,
  Grid,
  Header,
  Icon,
  Loader,
  Message,
  Segment,
} from 'semantic-ui-react'
import { getTaskApprovalText } from './task-approval-table-cell'
import { TaskAssignedToNode } from './task-assigned-to-node'

interface TaskRequestFromProps {
  request: TaskRequest
}

export const TaskRequestFromCard = ({ request }: TaskRequestFromProps) => {
  const { isLoading, isError, data } = useGetTaskQuery({
    id: request.from_task_id,
  })
  return (
    <Card fluid>
      <Card.Content header="Requesting task" />
      <Card.Content>
        <RequestingTask isLoading={isLoading} isError={isError} task={data} />
      </Card.Content>
    </Card>
  )
}

interface RequestingTaskProps {
  isLoading: boolean
  isError: boolean
  task: Task | undefined
}

const RequestingTask = ({ isLoading, isError, task }: RequestingTaskProps) => {
  if (isLoading) {
    return (
      <Segment basic>
        <Loader active />
      </Segment>
    )
  }

  if (isError || !task) {
    return (
      <Message negative icon>
        <Icon name="exclamation" size="mini" />
        <Message.Content>
          <Message.Header>Oops! There was an error</Message.Header>
          Failed to load requesting task.
        </Message.Content>
      </Message>
    )
  }

  const text = getTaskApprovalText(task)
  return (
    <Grid>
      <Grid.Row columns={1}>
        <Grid.Column>
          <a href={task.url}>{task.name}</a>
        </Grid.Column>
      </Grid.Row>
      <Grid.Row columns={2}>
        <Grid.Column>
          <Header sub>Assigned to</Header>
          <TaskAssignedToNode task={task} />
        </Grid.Column>
        <Grid.Column>
          <Header sub>Approval?</Header>
          {text}
        </Grid.Column>
      </Grid.Row>
    </Grid>
  )
}
