import { EditorEvents, RichTextArea } from 'comps/rich-text'
import { ModalProps } from 'comps/task/task-action-card'
import React, { useEffect, useState } from 'react'
import { Button, Form, Modal } from 'semantic-ui-react'

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
          <Form.Input readOnly>{lawyer?.full_name}</Form.Input>
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
