import api from 'api'
import { enqueueSnackbar } from 'notistack'
import React, { useEffect, useMemo, useState } from 'react'
import { Card, Dropdown, Grid, Header } from 'semantic-ui-react'
import { TaskDetailProps } from 'types/task'
import { choiceToMap, getAPIErrorMessage } from 'utils'

export const TaskMetaCard = ({
  choices,
  perms,
  setTask,
  task,
  update,
}: TaskDetailProps) => {
  const [users, setUsers] = useState([])
  const [isUsersLoading, setIsUsersLoading] = useState(false)
  const [getUsers] = api.useLazyGetUsersQuery()

  const statusMap = useMemo(() => choiceToMap(choices.status), [])

  useEffect(() => {
    setIsUsersLoading(true)
    getUsers({ isActive: true, sort: 'email' })
      .unwrap()
      .then((users) => {
        setUsers(users)
        setIsUsersLoading(false)
      })
      .catch(() => setIsUsersLoading(false))
  }, [])

  const handleChange = (name: string, value: any) => {
    update({ [name]: value })
      .then((instance) => {
        enqueueSnackbar('Updated task', { variant: 'success' })
        setTask(instance)
      })
      .catch((err) => {
        enqueueSnackbar(getAPIErrorMessage(err, 'Failed to update this task'), {
          variant: 'error',
        })
      })
  }

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
              <Dropdown
                search
                disabled={!perms.is_paralegal_or_better}
                selectOnNavigation={false}
                loading={isUsersLoading}
                value={task.assigned_to ? task.assigned_to.id : ''}
                options={users.map((u) => ({
                  key: u.id,
                  value: u.id,
                  text: u.email,
                }))}
                onChange={(e, { value }) =>
                  handleChange('assigned_to_id', value)
                }
              />
            </Grid.Column>
          </Grid.Row>
          <Grid.Row columns={1}>
            <Grid.Column>
              <Header sub>Owner</Header>
              <Dropdown
                search
                disabled={!perms.is_coordinator_or_better}
                selectOnNavigation={false}
                loading={isUsersLoading}
                value={task.owner ? task.owner.id : ''}
                options={users.map((u) => ({
                  key: u.id,
                  value: u.id,
                  text: u.email,
                }))}
                onChange={(e, { value }) => handleChange('owner_id', value)}
              />
            </Grid.Column>
          </Grid.Row>
        </Grid>
      </Card.Content>
    </Card>
  )
}
