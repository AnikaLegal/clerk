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
import { Button, Card, Form, List, Modal } from 'semantic-ui-react'
import { TaskDetailProps, TaskStatus } from 'types/task'
import { getAPIErrorMessage } from 'utils'

interface TaskActionProps extends Omit<TaskDetailProps, 'choices'> {
  status: TaskStatus
}

interface ModalProps extends TaskActionProps {
  onClose: () => void
  open: boolean
}

interface TaskOptionBase {
  id: string
  icon: string
  text: string
  when: () => boolean
}
interface TaskActionOption extends TaskOptionBase {
  action: () => void
  modal?: never
}
interface TaskModalOption extends TaskOptionBase {
  action?: never
  modal: React.FC<ModalProps>
}
type TaskOption = TaskActionOption | TaskModalOption

interface TaskModalProps extends TaskActionProps {
  option: TaskOption
}

export const TaskActionCard = ({
  perms,
  setTask,
  status,
  task,
  update,
}: TaskActionProps) => {
  const handleChange = (name: string, value: any) => {
    update({ [name]: value })
      .then((instance) => {
        enqueueSnackbar('Updated task', { variant: 'success' })
        setTask(instance)
      })
      .catch((e) => {
        enqueueSnackbar(getAPIErrorMessage(e, 'Failed to update task'), {
          variant: 'error',
        })
      })
  }

  const options: TaskOption[] = [
    {
      id: 'reopen',
      icon: 'undo',
      text: 'Reopen the task',
      when: () => perms.is_paralegal_or_better && !task.is_open,
      action: () => handleChange('status', status.stopped),
    },
    {
      id: 'start',
      icon: 'play circle outline',
      text: 'Start the task',
      when: () => perms.is_paralegal_or_better && task.status === status.stopped,
      action: () => handleChange('status', status.started),
    },
    {
      id: 'stop',
      icon: 'stop circle outline',
      text: 'Stop the task',
      when: () => perms.is_paralegal_or_better && task.status === status.started,
      action: () => handleChange('status', status.stopped),
    },
    {
      id: 'finish',
      icon: 'check',
      text: 'Finish the task',
      when: () => perms.is_paralegal_or_better && task.is_open,
      action: () => handleChange('status', status.finished),
    },
    {
      id: 'cancel',
      icon: 'close',
      text: 'Cancel the task',
      when: () => perms.is_paralegal_or_better && task.is_open,
      modal: CancelTaskModal,
    },
  ]

  return (
    <Card fluid>
      <Card.Content>
        <List verticalAlign="middle" selection>
          {options
            .filter((o) => o.when())
            .map((option) =>
              option.action ? (
                <TaskAction key={option.id} option={option} />
              ) : (
                <TaskModal
                  key={option.id}
                  option={option}
                  task={task}
                  setTask={setTask}
                  update={update}
                  perms={perms}
                  status={status}
                />
              )
            )}
        </List>
      </Card.Content>
    </Card>
  )
}

export const TaskAction = ({ option }: { option: TaskOption }) => {
  return (
    <List.Item key={option.id} onClick={option.action}>
      <List.Content>
        <div className="header">
          <i className={`${option.icon} icon`}></i>
          {option.text}
        </div>
      </List.Content>
    </List.Item>
  )
}

export const TaskModal = ({ option, ...props }: TaskModalProps) => {
  const [open, setOpen] = useState(false)

  return (
    <>
      <List.Item key={option.id} onClick={() => setOpen(true)}>
        <List.Content>
          <div className="header">
            <i className={`${option.icon} icon`}></i>
            {option.text}
          </div>
        </List.Content>
      </List.Item>
      <option.modal
        {...props}
        open={open}
        onClose={() => {
          setOpen(false)
        }}
      />
    </>
  )
}

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
