import api, { User } from 'api'
import { EditorEvents, RichTextArea } from 'comps/rich-text'
import { ModalProps } from 'comps/task/task-action-card'
import { enqueueSnackbar } from 'notistack'
import React, { useEffect, useState } from 'react'
import { Button, Dropdown, Form, Modal } from 'semantic-ui-react'
import { getAPIErrorMessage } from 'utils'

export const CancelTaskModal: React.FC<ModalProps> = ({
  task,
  setTask,
  update,
  status,
  open,
  onClose,
}) => {
  const [canSubmit, setCanSubmit] = useState<boolean>(false)
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false)
  const [createComment] = api.useCreateTaskCommentMutation()
  const [text, setText] = useState<string>('')

  useEffect(() => {
    setCanSubmit(text != '')
  }, [text])

  const handleUpdate = ({ editor }: EditorEvents['update']) => {
    if (editor) {
      setText(editor.isEmpty || editor.getText() == '' ? '' : editor.getHTML())
    }
  }

  const handleSubmit = (e) => {
    e.stopPropagation()
    setIsSubmitting(true)

    Promise.all([
      update({ status: status.cancelled }),
      createComment({ id: task.id, taskCommentCreate: { text: text } }),
    ])
      .then((results) => {
        enqueueSnackbar('Cancelled task', { variant: 'success' })
        setTask(results[0])
      })
      .catch((e) => {
        enqueueSnackbar(getAPIErrorMessage(e, 'Failed to cancel task'), {
          variant: 'error',
        })
      })
    setIsSubmitting(false)
    onClose()
  }

  return (
    <Modal
      as="Form"
      className="form"
      open={open}
      onClose={onClose}
      onSubmit={(e) => handleSubmit(e)}
      size="tiny"
    >
      <Modal.Header>Cancel the task</Modal.Header>
      <Modal.Content>
        <Form.Field required>
          <label>Briefly explain why the task was not completed</label>
          <RichTextArea autoFocus onUpdate={handleUpdate} />
        </Form.Field>
      </Modal.Content>
      <Modal.Actions>
        <Button type="button" onClick={onClose} disabled={isSubmitting}>
          Close
        </Button>
        <Button
          primary
          type="submit"
          loading={isSubmitting}
          disabled={isSubmitting || !canSubmit}
        >
          Cancel task
        </Button>
      </Modal.Actions>
    </Modal>
  )
}

export const ReassignTaskModal: React.FC<ModalProps> = ({
  task,
  setTask,
  update,
  status,
  open,
  onClose,
}) => {
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false)
  const [userId, setUserId] = useState<number>()

  const userResults = api.useGetUsersQuery({ isActive: true, sort: 'email' })
  const users = userResults.data || []

  const handleSubmit = (e) => {
    e.stopPropagation()
    setIsSubmitting(true)
    update({ assigned_to_id: userId })
      .then((instance) => {
        enqueueSnackbar('Updated task', { variant: 'success' })
        setTask(instance)
      })
      .catch((err) => {
        enqueueSnackbar(getAPIErrorMessage(err, 'Failed to update this task'), {
          variant: 'error',
        })
      })
    setIsSubmitting(false)
    onClose()
  }

  useEffect(() => {
    setUserId(task.assigned_to?.id)
  }, [open])

  return (
    <Modal
      as="Form"
      className="form"
      open={open}
      onClose={onClose}
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
            options={users.map((u) => ({
              key: u.id,
              value: u.id,
              text: u.email,
            }))}
            search
            searchInput={{ autoFocus: true }}
            selection
            value={userId || ''}
          />
        </Form.Field>
      </Modal.Content>
      <Modal.Actions>
        <Button type="button" onClick={onClose} disabled={isSubmitting}>
          Close
        </Button>
        <Button
          primary
          type="submit"
          loading={isSubmitting}
          disabled={isSubmitting || !userId || userId === task.assigned_to?.id}
        >
          Reassign task
        </Button>
      </Modal.Actions>
    </Modal>
  )
}

export const QuestionModal: React.FC<ModalProps> = ({
  task,
  setTask,
  update,
  status,
  open,
  onClose,
}) => {
  const [canSubmit, setCanSubmit] = useState<boolean>(false)
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false)
  const [userId, setUserId] = useState<number>()
  const [text, setText] = useState<string>('')

  useEffect(() => {
    setCanSubmit(text != '')
  }, [text])

  const paralegal = task.issue.paralegal
  const lawyer = task.issue.lawyer

  const userResults = api.useGetUsersQuery({ isActive: true })

  const caseUserOptions: User[] = [paralegal, lawyer]
    .filter((u) => u)
    .filter(({ full_name }) => full_name)
    .filter(({ id }) => id !== task.assigned_to.id)

  const otherUserOptions: User[] = (userResults.data || [])
    .filter(({ id }) => !caseUserOptions.find((u) => id === u.id))
    .filter(({ id }) => id !== task.assigned_to.id)
    .filter(({ full_name }) => full_name)
    .sort((a, b) => a.full_name.localeCompare(b.full_name))

  const handleSubmit = (e) => {
    e.stopPropagation()
    setIsSubmitting(true)
    setIsSubmitting(false)
    onClose()
  }

  const handleUpdate = ({ editor }: EditorEvents['update']) => {
    if (editor) {
      setText(editor.isEmpty || editor.getText() == '' ? '' : editor.getHTML())
    }
  }

  return (
    <Modal
      as="Form"
      className="form"
      open={open}
      onClose={onClose}
      onSubmit={(e) => handleSubmit(e)}
      size="tiny"
    >
      <Modal.Header>Ask a question about this task</Modal.Header>
      <Modal.Content>
        <Form.Field required>
          <label>To</label>
          <Dropdown
            fluid
            search
            selection
            loading={userResults.isLoading}
            onChange={(e, { value }) => setUserId(value as number)}
            openOnFocus={false}
            value={userId || lawyer?.id || ''}
            options={[...caseUserOptions, ...otherUserOptions].map((u) => ({
              key: u.id,
              value: u.id,
              text: u.full_name,
              description:
                (paralegal && u.id === paralegal.id && 'Paralegal') ||
                (lawyer && u.id === lawyer.id && 'Case Lawyer') ||
                '',
            }))}
          />
        </Form.Field>
        <Form.Field required>
          <label>Question</label>
          <RichTextArea autoFocus onUpdate={handleUpdate} />
        </Form.Field>
      </Modal.Content>
      <Modal.Actions>
        <Button type="button" onClick={onClose} disabled={isSubmitting}>
          Close
        </Button>
        <Button
          primary
          type="submit"
          loading={isSubmitting}
          disabled={isSubmitting || !canSubmit}
        >
          Send
        </Button>
      </Modal.Actions>
    </Modal>
  )
}
