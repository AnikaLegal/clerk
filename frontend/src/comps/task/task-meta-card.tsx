import React, { useState, useMemo, useEffect } from 'react'
import api, { Task } from 'api'
import { Header, Grid, Dropdown, Card } from 'semantic-ui-react'
import { getAPIErrorMessage, choiceToOptions } from 'utils'
import { useSnackbar } from 'notistack'
import { TaskDetailProps } from 'types'

export const TaskMetaCard = ({
  task,
  setTask,
  update,
  choices,
  perms,
}: TaskDetailProps) => {
  const [users, setUsers] = useState([])
  const [isUsersLoading, setIsUsersLoading] = useState(false)
  const [getUsers] = api.useLazyGetUsersQuery()

  const statusOptions = useMemo(() => choiceToOptions(choices.status), [])
  const { enqueueSnackbar } = useSnackbar()

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
        enqueueSnackbar(`Updated task`, { variant: 'success' })
        setTask(instance)
      })
      .catch((err) => {
        enqueueSnackbar(getAPIErrorMessage(err, `Failed to update this task`), {
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
              <Dropdown
                value={task.status}
                options={statusOptions}
                onChange={(e, { value }) => handleChange('status', value)}
              />
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
                value={task.assigned_to.id}
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
                value={task.owner.id}
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