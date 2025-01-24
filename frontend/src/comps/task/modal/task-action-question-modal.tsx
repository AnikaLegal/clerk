import api, { User } from 'api'
import { EditorEvents, RichTextArea } from 'comps/rich-text'
import { ModalProps } from 'comps/task/task-action-card'
import React, { useEffect, useState } from 'react'
import { Button, Dropdown, Form, Modal } from 'semantic-ui-react'

export const QuestionModal = (props: ModalProps) => {
  const [canSubmit, setCanSubmit] = useState<boolean>(false)
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false)
  const [userId, setUserId] = useState<number>()
  const [text, setText] = useState<string>('')

  useEffect(() => {
    setCanSubmit(text != '')
  }, [text])

  const assignee = props.task.assigned_to
  const paralegal = props.task.issue.paralegal
  const lawyer = props.task.issue.lawyer
  const currentUser = props.user

  const userResults = api.useGetUsersQuery({ isActive: true })
  const users: User[] = [
    ...(userResults.data || []),
    ...(lawyer ? [lawyer] : []),
  ]
    .filter(
      ({ id, is_coordinator_or_better }) =>
        id != currentUser.id &&
        (id == assignee?.id ||
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
