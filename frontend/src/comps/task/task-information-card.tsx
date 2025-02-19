import { Task } from 'api'
import moment from 'moment'
import React, { useMemo } from 'react'
import { Card, Grid, Header } from 'semantic-ui-react'
import { ModelChoices } from 'types/global'
import { choiceToMap } from 'utils'

interface TaskInformationCardProps {
  choices: ModelChoices
  task: Task
}

export const TaskInformationCard = ({
  choices,
  task,
}: TaskInformationCardProps) => {
  const statusMap = useMemo(() => choiceToMap(choices.status), [])

  return (
    <Card fluid>
      <Card.Content header="Task information" />
      <Card.Content>
        <Grid>
          <Grid.Row columns={2}>
            <Grid.Column>
              <Header sub>Assigned To</Header>
              {task.assigned_to ? (
                <a href={task.assigned_to.url}>{task.assigned_to.full_name}</a>
              ) : (
                '-'
              )}
            </Grid.Column>
            <Grid.Column>
              <Header sub>Status</Header>
              {statusMap.get(task.status)}
            </Grid.Column>
          </Grid.Row>
          <Grid.Row columns={2}>
            <Grid.Column>
              <Header sub>Date Created</Header>
              {moment(task.created_at).format('DD/MM/YYYY')}
            </Grid.Column>
            <Grid.Column>
              <Header sub>Date Due</Header>
              {task.due_at || '-'}
            </Grid.Column>
          </Grid.Row>
          <Grid.Row columns={2}>
            <Grid.Column>
              <Header sub>Date Closed</Header>
              {task.closed_at
                ? moment(task.closed_at).format('DD/MM/YYYY')
                : '-'}
            </Grid.Column>
            <Grid.Column>
              <Header sub>Days Open</Header>
              {task.days_open}
            </Grid.Column>
          </Grid.Row>
        </Grid>
      </Card.Content>
    </Card>
  )
}
