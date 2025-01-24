import api, { User } from 'api'
import { EditorEvents, RichTextArea } from 'comps/rich-text'
import { ModalProps } from 'comps/task/task-action-card'
import { enqueueSnackbar } from 'notistack'
import React, { useEffect, useState } from 'react'
import { Button, Dropdown, Form, Modal } from 'semantic-ui-react'
import { getAPIErrorMessage } from 'utils'

export const CancelTaskModal = (props: ModalProps) => {
  const [canSubmit, setCanSubmit] = useState<boolean>(false)
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false)
  const [createComment] = api.useCreateTaskCommentMutation()
  const [text, setText] = useState<string>('')

  useEffect(() => {
    setCanSubmit(text != '')
  }, [text])

  const handleClose = () => {
    setText('')
    props.onClose()
  }

  const handleUpdate = ({ editor }: EditorEvents['update']) => {
    if (editor) {
      setText(editor.isEmpty || editor.getText() == '' ? '' : editor.getHTML())
    }
  }

  const handleSubmit = (event) => {
    event.stopPropagation()

    setIsSubmitting(true)
    props
      .update({ status: props.status.cancelled })
      .then((instance) => {
        props.setTask(instance)
        createComment({
          id: props.task.id,
          taskCommentCreate: { text: text, creator_id: props.user.id },
        })
          .then((instance) => {})
          .catch((e) => {
            enqueueSnackbar(
              getAPIErrorMessage(e, 'Cancelled task but failed to add comment'),
              {
                variant: 'error',
              }
            )
          })
      })
      .catch((e) => {
        enqueueSnackbar(getAPIErrorMessage(e, 'Failed to cancel task'), {
          variant: 'error',
        })
      })
      .finally(() => {
        setIsSubmitting(false)
      })
    handleClose()
  }

  return (
    <Modal
      as="Form"
      className="form"
      open={props.open}
      onClose={handleClose}
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

export const ReassignTaskModal = (props: ModalProps) => {
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false)
  const [userId, setUserId] = useState<number>()

  const userResults = api.useGetUsersQuery({ isActive: true, sort: 'email' })
  const users: User[] = userResults.data?.filter(
    ({ id, is_coordinator_or_better }) =>
      id == props.task.assigned_to?.id ||
      id == props.task.issue.paralegal?.id ||
      is_coordinator_or_better
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

export const QuestionModal = (props: ModalProps) => {
  const [canSubmit, setCanSubmit] = useState<boolean>(false)
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false)
  const [userId, setUserId] = useState<number>()
  const [text, setText] = useState<string>('')

  useEffect(() => {
    setCanSubmit(text != '')
  }, [text])

  const paralegal = props.task.issue.paralegal
  const lawyer = props.task.issue.lawyer

  const userResults = api.useGetUsersQuery({ isActive: true })
  const users: User[] = [
    ...(userResults.data || []),
    ...(lawyer ? [lawyer] : []),
  ]
    .filter(
      ({ id, is_coordinator_or_better }) =>
        id != props.user.id &&
        (id == props.task.assigned_to?.id ||
          id == paralegal?.id ||
          id == lawyer?.id ||
          is_coordinator_or_better)
    )
    .sort((a, b) => a.full_name.localeCompare(b.full_name))

  const handleClose = () => {
    setText('')
    props.onClose()
  }

  const handleSubmit = (e) => {
    e.stopPropagation()
    setIsSubmitting(true)
    setIsSubmitting(false)
    handleClose()
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
      open={props.open}
      onClose={handleClose}
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
            options={
              users?.map((u) => ({
                key: u.id,
                value: u.id,
                text: u.full_name || u.email,
                description:
                  (paralegal && u.id === paralegal.id && 'Paralegal') ||
                  (lawyer && u.id === lawyer.id && 'Case Lawyer') ||
                  '',
              })) || []
            }
          />
        </Form.Field>
        <Form.Field required>
          <label>Question</label>
          <RichTextArea autoFocus onUpdate={handleUpdate} />
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

export const RequestApprovalModal = (props: ModalProps) => {
  const [canSubmit, setCanSubmit] = useState<boolean>(false)
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false)
  const [text, setText] = useState<string>('')

  useEffect(() => {
    setCanSubmit(text != '')
  }, [text])

  const handleClose = () => {
    setText('')
    props.onClose()
  }

  const handleSubmit = (event) => {
    event.stopPropagation()
    setIsSubmitting(true)
    setIsSubmitting(false)
    handleClose()
  }

  const handleUpdate = ({ editor }: EditorEvents['update']) => {
    if (editor) {
      setText(editor.isEmpty || editor.getText() == '' ? '' : editor.getHTML())
    }
  }

  const lawyer = props.task.issue.lawyer

  return (
    <Modal
      as="Form"
      className="form"
      open={props.open}
      onClose={handleClose}
      onSubmit={(e) => handleSubmit(e)}
      size="tiny"
    >
      <Modal.Header>Request approval for this task</Modal.Header>
      <Modal.Content>
        <Form.Field>
          <label>Requesting approval from</label>
          <Form.Input readOnly>{lawyer.full_name}</Form.Input>
        </Form.Field>
        <Form.Field required>
          <label>Briefly explain what you are requesting approval for</label>
          <RichTextArea autoFocus onUpdate={handleUpdate} />
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
          Request approval
        </Button>
      </Modal.Actions>
    </Modal>
  )
}
