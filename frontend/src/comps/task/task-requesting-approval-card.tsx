import { Task, TaskList } from 'api'
import React, { useMemo } from 'react'
import { Card, Grid, Header } from 'semantic-ui-react'
import { ModelChoices } from 'types/global'
import { choiceToMap } from 'utils'
import { getApprovalTextAndColor } from './task-approval-table-cell'

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
  const [text, _] = getApprovalTextAndColor(task as TaskList)

  return (
    <Card fluid>
      <Card.Content header="Requesting task" />
      <Card.Content>
        <Grid>
          <Grid.Row columns={1}>
            <Grid.Column>
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
              <Header sub>Approval?</Header>
              {text}
            </Grid.Column>
          </Grid.Row>
        </Grid>
      </Card.Content>
    </Card>
  )
}
