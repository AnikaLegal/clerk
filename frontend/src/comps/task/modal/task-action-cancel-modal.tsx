import api from 'api'
import { EditorEvents, RichTextArea } from 'comps/rich-text'
import { ModalProps } from 'comps/task/task-action-card'
import { enqueueSnackbar } from 'notistack'
import React, { useEffect, useState } from 'react'
import { Button, Form, Modal } from 'semantic-ui-react'
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
      .then((task) => {
        props.setTask(task)
        createComment({
          id: props.task.id,
          taskCommentCreate: { text: text, creator_id: props.user.id },
        })
          .then((comment) =>
            enqueueSnackbar('Cancelled task', { variant: 'success' })
          )
          .catch((e) =>
            enqueueSnackbar(
              getAPIErrorMessage(e, 'Cancelled task but failed to add comment'),
              {
                variant: 'error',
              }
            )
          )
      })
      .catch((e) => {
        enqueueSnackbar(getAPIErrorMessage(e, 'Failed to cancel task'), {
          variant: 'error',
        })
      })
      .finally(() => setIsSubmitting(false))
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
