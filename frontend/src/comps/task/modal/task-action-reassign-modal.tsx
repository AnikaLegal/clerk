import api, { User } from 'api'
import { ModalProps } from 'comps/task/task-action-card'
import { enqueueSnackbar } from 'notistack'
import React, { useEffect, useState } from 'react'
import { Button, Dropdown, Form, Modal } from 'semantic-ui-react'
import { getAPIErrorMessage } from 'utils'

export const ReassignTaskModal = (props: ModalProps) => {
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false)
  const [userId, setUserId] = useState<number>()

  const assignee = props.task.assigned_to
  const paralegal = props.task.issue.paralegal

  const userResults = api.useGetUsersQuery({ isActive: true, sort: 'email' })
  const users: User[] = userResults.data?.filter(
    ({ id, is_coordinator_or_better }) =>
      id == assignee?.id || id == paralegal?.id || is_coordinator_or_better
  )

  const handleSubmit = (event) => {
    event.stopPropagation()

    setIsSubmitting(true)
    props
      .update({ assigned_to_id: userId })
      .then((instance) => {
        enqueueSnackbar('Updated task', { variant: 'success' })
        props.setTask(instance)
      })
      .catch((e) => {
        enqueueSnackbar(getAPIErrorMessage(e, 'Failed to update task'), {
          variant: 'error',
        })
      })
    setIsSubmitting(false)
    props.onClose()
  }

  useEffect(() => {
    setUserId(props.task.assigned_to?.id)
  }, [open])

  return (
    <Modal
      as="Form"
      className="form"
      open={props.open}
      onClose={props.onClose}
      onSubmit={(e) => handleSubmit(e)}
      size="tiny"
    >
      <Modal.Header>Reassign the task</Modal.Header>
      <Modal.Content>
        <Form.Field required>
          <label>Assign To</label>
          <Dropdown
            fluid
            loading={userResults.isLoading}
            onChange={(e, { value }) => setUserId(value as number)}
            openOnFocus={false}
            options={
              users?.map((u) => ({
                key: u.id,
                value: u.id,
                text: u.email,
              })) || []
            }
            search
            searchInput={{ autoFocus: true }}
            selection
            value={userId || ''}
          />
        </Form.Field>
      </Modal.Content>
      <Modal.Actions>
        <Button type="button" onClick={props.onClose} disabled={isSubmitting}>
          Close
        </Button>
        <Button
          primary
          type="submit"
          loading={isSubmitting}
          disabled={
            isSubmitting || !userId || userId === props.task.assigned_to?.id
          }
        >
          Reassign task
        </Button>
      </Modal.Actions>
    </Modal>
  )
}
