import { Task } from 'api'
import { TASK_STATUSES } from 'consts'
import moment from 'moment'
import React from 'react'
import { Card, Grid, Header } from 'semantic-ui-react'
import { TaskAssignedToNode } from './task-assigned-to-node'

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
    </Card>
  )
}
