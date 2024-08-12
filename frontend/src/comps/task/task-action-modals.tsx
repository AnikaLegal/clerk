import api, { TaskCommentCreate } from 'api'
import {
  EditorExtensions,
  Placeholder,
  resetEditor,
  RichTextCommentEditor,
  useEditor,
} from 'comps/richtext-editor'
import { enqueueSnackbar } from 'notistack'
import React, { useEffect, useState } from 'react'
import { Button, Form, Modal } from 'semantic-ui-react'
import { getAPIErrorMessage } from 'utils'
import { ModalProps } from 'comps/task/task-action-card'

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
