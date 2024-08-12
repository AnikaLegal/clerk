import React, { useMemo } from 'react'
import { Card, Grid, Header } from 'semantic-ui-react'
import { TaskDetailProps } from 'types/task'
import { choiceToMap } from 'utils'

export const TaskMetaCard = ({
  choices,
  perms,
  setTask,
  task,
  update,
}: TaskDetailProps) => {
  const statusMap = useMemo(() => choiceToMap(choices.status), [])

  return (
    <Card fluid>
      <Card.Content>
        <Grid>
          <Grid.Row columns={2}>
            <Grid.Column>
              <Header sub>Status</Header>
              {statusMap.get(task.status)}
            </Grid.Column>
            <Grid.Column>
              <Header sub>Days Open</Header>
              {task.days_open}
            </Grid.Column>
          </Grid.Row>
          <Grid.Row columns={2}>
            <Grid.Column>
              <Header sub>Date Created</Header>
              {task.created_at}
            </Grid.Column>
            <Grid.Column>
              <Header sub>Date Closed</Header>
              {task.closed_at || '-'}
            </Grid.Column>
          </Grid.Row>
          <Grid.Row columns={1}>
            <Grid.Column>
              <Header sub>Assigned To</Header>
              {task.assigned_to ? (
                <a href={task.assigned_to.url}>{task.assigned_to.full_name}</a>
              ) : (
                '-'
              )}
            </Grid.Column>
          </Grid.Row>
        </Grid>
      </Card.Content>
    </Card>
  )
}
