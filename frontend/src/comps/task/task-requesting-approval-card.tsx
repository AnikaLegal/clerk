import { Task } from 'api'
import React, { useMemo } from 'react'
import { Card, Grid, Header } from 'semantic-ui-react'
import { ModelChoices } from 'types/global'
import { choiceToMap } from 'utils'

interface TaskRequestingApprovalCardProps {
  choices: ModelChoices
  task: Task
}

export const TaskRequestingApprovalCard = ({
  choices,
  task,
}: TaskRequestingApprovalCardProps) => {
  const statusMap = useMemo(() => choiceToMap(choices.status), [])
  if (!task) {
    return null
  }
  return (
    <Card fluid>
      <Card.Content header="Requesting task" />
      <Card.Content>
        <Grid>
          <Grid.Row columns={1}>
            <Grid.Column>
              <Header sub>Name</Header>
              <a href={task.url}>{task.name}</a>
            </Grid.Column>
          </Grid.Row>
          <Grid.Row columns={2}>
            <Grid.Column>
              <Header sub>Assigned to</Header>
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
        </Grid>
      </Card.Content>
    </Card>
  )
}
