import api, { TaskCommentCreate, User } from 'api'
import {
  EditorExtensions,
  Placeholder,
  resetEditor,
  RichTextCommentEditor,
  useEditor,
} from 'comps/richtext-editor'
import { ModalProps, TaskModal } from 'comps/task/task-action-card'
import { enqueueSnackbar } from 'notistack'
import React, { useEffect, useState, useRef } from 'react'
import {
  Button,
  Dropdown,
  DropdownItemProps,
  Form,
  Modal,
} from 'semantic-ui-react'
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

  const editor = useEditor({ extensions: [...EditorExtensions, Placeholder] })

  const handleClose = () => {
    resetEditor(editor)
    onClose()
  }

  const handleSubmit = (e) => {
    e.stopPropagation()
    setIsSubmitting(true)

    const values: TaskCommentCreate = {
      text: editor.getHTML(),
    }

    Promise.all([
      update({ status: status.cancelled }),
      createComment({ id: task.id, taskCommentCreate: values }),
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
    handleClose()
  }

  useEffect(() => {
    if (editor && open) {
      editor.commands.focus()
    }
  }, [open])

  useEffect(() => {
    if (editor) {
      const handleEditorUpdate = () => {
        setCanSubmit(!editor.isEmpty && editor.getText().trim() != '')
      }
      editor.on('update', handleEditorUpdate)
    }
  }, [editor])

  return (
    <Modal
      as="Form"
      centered={false}
      className="form"
      open={open}
      onClose={handleClose}
      onSubmit={(e) => handleSubmit(e)}
      size="tiny"
    >
      <Modal.Header>Cancel the task</Modal.Header>
      <Modal.Content>
        <Form.Field required>
          <label>Briefly explain why the task was not completed</label>
          <RichTextCommentEditor editor={editor} />
        </Form.Field>
      </Modal.Content>
      <Modal.Actions>
        <Button type="button" onClick={handleClose} disabled={isSubmitting}>
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
      centered={false}
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

  const userResults = api.useGetUsersQuery({ isActive: true })

  const paralegal = task.issue.paralegal
  const lawyer = task.issue.lawyer

  const caseUserOptions: User[] = [paralegal, lawyer]
    .filter((u) => u)
    .filter(({ full_name }) => full_name)
    .filter(({ id }) => id !== task.assigned_to.id)

  const otherUserOptions: User[] = (userResults.data || [])
    .filter(({ id }) => !caseUserOptions.find((u) => id === u.id))
    .filter(({ id }) => id !== task.assigned_to.id)
    .filter(({ full_name }) => full_name)
    .sort((a, b) => a.full_name.localeCompare(b.full_name))

  const handleClose = () => {
    setUserId(null)
    resetEditor(editor)
    onClose()
  }

  const handleSubmit = (e) => {
    e.stopPropagation()
    setIsSubmitting(true)
    setIsSubmitting(false)
    handleClose()
  }

  const editor = useEditor({ extensions: EditorExtensions })

  const handleUpdates = () => {
    setCanSubmit(userId && !editor.isEmpty && editor.getText().trim() != '')
  }
  useEffect(handleUpdates, [editor, userId])

  useEffect(() => {
    if (editor) editor.on('update', handleUpdates)
  }, [editor, userId])

  return (
    <Modal
      as="Form"
      centered={false}
      className="form"
      open={open}
      onClose={handleClose}
      onSubmit={(e) => handleSubmit(e)}
      size="tiny"
    >
      <Modal.Header>Ask a question about this task</Modal.Header>
      <Modal.Content>
        <Form.Field>
          <label>To</label>
          <Dropdown
            fluid
            search
            selection
            loading={userResults.isLoading}
            onChange={(e, { value }) => setUserId(value as number)}
            openOnFocus={false}
            searchInput={{ autoFocus: true }}
            value={userId || ''}
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
        <Form.Field>
          <label>Question</label>
          <RichTextCommentEditor editor={editor} />
        </Form.Field>
      </Modal.Content>
      <Modal.Actions>
        <Button type="button" onClick={handleClose} disabled={isSubmitting}>
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
