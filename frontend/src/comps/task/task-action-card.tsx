import { enqueueSnackbar } from 'notistack'
import React, { useState } from 'react'
import { Button, Card, Icon, List, SemanticICONS } from 'semantic-ui-react'
import { TaskDetailProps, TaskStatus } from 'types/task'
import { getAPIErrorMessage } from 'utils'
import { CancelTaskModal, ReassignTaskModal, QuestionModal } from 'comps/task'
import { TextButton } from 'comps/button'

export interface ModalProps extends TaskActionProps {
  onClose: () => void
  open: boolean
}

interface TaskActionProps extends Omit<TaskDetailProps, 'choices'> {
  status: TaskStatus
}

interface TaskOptionBase {
  id: string
  icon: SemanticICONS
  text: string
  showWhen: () => boolean
  disableWhen?: () => boolean
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
      showWhen: () => perms.is_paralegal_or_better && !task.is_open,
      action: () => handleChange('status', status.stopped),
    },
    {
      id: 'start',
      icon: 'play',
      text: 'Start the task',
      showWhen: () =>
        perms.is_paralegal_or_better && task.status === status.stopped,
      action: () => handleChange('status', status.started),
    },
    {
      id: 'stop',
      icon: 'stop',
      text: 'Stop the task',
      showWhen: () =>
        perms.is_paralegal_or_better && task.status === status.started,
      action: () => handleChange('status', status.stopped),
    },
    {
      id: 'complete',
      icon: 'check',
      text: 'Complete the task',
      showWhen: () => perms.is_paralegal_or_better && task.is_open,
      disableWhen: () => task.is_approval_required && !task.is_approved,
      action: () => handleChange('status', status.finished),
    },
    {
      id: 'cancel',
      icon: 'close',
      text: 'Cancel the task',
      showWhen: () => perms.is_paralegal_or_better && task.is_open,
      disableWhen: () => task.is_approval_required && !task.is_approved,
      modal: CancelTaskModal,
    },
    {
      id: 'reassign',
      icon: 'user',
      text: 'Reassign the task',
      showWhen: () => perms.is_coordinator_or_better && task.is_open,
      modal: ReassignTaskModal,
    },
    {
      id: 'question',
      icon: 'question',
      text: 'Ask a question',
      showWhen: () => perms.is_paralegal_or_better && task.is_open,
      modal: QuestionModal,
    },
  ]

  return (
    <Card fluid>
      <Card.Content header="Task actions" />
      <Card.Content>
        <List verticalAlign="middle" selection>
          {options
            .filter((o) => o.showWhen())
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
  const disabled = option.disableWhen && option.disableWhen()
  return (
    <List.Item key={option.id}>
      <List.Content>
        <List.Header>
          <TextButton icon disabled={disabled} onClick={option.action}>
            <span>
              <Icon name={option.icon} />
              {option.text}
            </span>
          </TextButton>
        </List.Header>
      </List.Content>
    </List.Item>
  )
}

export const TaskModal = ({ option, ...props }: TaskModalProps) => {
  const [open, setOpen] = useState(false)
  const disabled = option.disableWhen && option.disableWhen()

  return (
    <>
      <List.Item key={option.id}>
        <List.Content>
          <List.Header>
            <TextButton icon disabled={disabled} onClick={() => setOpen(true)}>
              <span>
                <Icon name={option.icon} />
                {option.text}
              </span>
            </TextButton>
          </List.Header>
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
