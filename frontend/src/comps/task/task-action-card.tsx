import { useUpdateTaskStatusMutation, TaskStatusUpdate } from 'api'
import { TextButton } from 'comps/button'
import {
  CancelTaskModal,
  QuestionModal,
  ReassignTaskModal,
  RequestApprovalModal,
} from 'comps/task'
import { enqueueSnackbar } from 'notistack'
import React, { useState } from 'react'
import { Card, Icon, List, SemanticICONS } from 'semantic-ui-react'
import { TaskDetailProps, TaskStatus } from 'types/task'
import { getAPIErrorMessage } from 'utils'

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

export const TaskActionCard = (props: TaskActionProps) => {
  const [updateTaskStatus] = useUpdateTaskStatusMutation()

  const updateStatusHandler = (values: TaskStatusUpdate) => {
    updateTaskStatus({ id: props.task.id, taskStatusUpdate: values })
      .unwrap()
      .then((task) => {
        props.setTask(task)
        enqueueSnackbar('Updated task status', { variant: 'success' })
      })
      .catch((e) => {
        enqueueSnackbar(getAPIErrorMessage(e, 'Failed to update task status'), {
          variant: 'error',
        })
      })
  }

  const perms = props.user
  const task = props.task
  const status = props.status

  const managementOptions: TaskOption[] = [
    {
      id: 'reopen',
      icon: 'undo',
      text: 'Reopen the task',
      showWhen: () => perms.is_paralegal_or_better && !task.is_open,
      action: () => updateStatusHandler({ status: status.stopped }),
    },
    {
      id: 'start',
      icon: 'play',
      text: 'Start the task',
      showWhen: () =>
        perms.is_paralegal_or_better && task.status === status.stopped,
      action: () => updateStatusHandler({ status: status.started }),
    },
    {
      id: 'stop',
      icon: 'stop',
      text: 'Stop the task',
      showWhen: () =>
        perms.is_paralegal_or_better && task.status === status.started,
      action: () => updateStatusHandler({ status: status.stopped }),
    },
    {
      id: 'approve',
      icon: 'thumbs up',
      text: 'Get approval',
      showWhen: () =>
        !perms.is_lawyer &&
        task.is_open &&
        task.is_approval_required &&
        !task.is_approved,
      modal: RequestApprovalModal,
    },
    {
      id: 'complete',
      icon: 'check',
      text: 'Complete the task',
      showWhen: () =>
        perms.is_paralegal_or_better &&
        task.is_open &&
        (perms.is_lawyer || !task.is_approval_required || task.is_approved),
      action: () => updateStatusHandler({ status: status.finished }),
    },
    {
      id: 'cancel',
      icon: 'close',
      text: 'Cancel the task',
      showWhen: () =>
        perms.is_paralegal_or_better &&
        task.is_open &&
        (perms.is_lawyer || !task.is_approval_required || task.is_approved),
      modal: CancelTaskModal,
    },
  ]

  const adminOptions: TaskOption[] = [
    {
      id: 'question',
      icon: 'question',
      text: 'Ask a question',
      showWhen: () => perms.is_paralegal_or_better && task.is_open,
      modal: QuestionModal,
    },
    {
      id: 'reassign',
      icon: 'user',
      text: 'Reassign the task',
      showWhen: () => perms.is_coordinator_or_better && task.is_open,
      modal: ReassignTaskModal,
    },
  ]

  return (
    <Card fluid>
      <Card.Content header="Task actions" />
      <TaskActionCardContent options={managementOptions} {...props} />
      <TaskActionCardContent options={adminOptions} {...props} />
    </Card>
  )
}

interface TaskActionCardContentProps extends TaskActionProps {
  options: TaskOption[]
}
export const TaskActionCardContent = (props: TaskActionCardContentProps) => {
  const visibleOptions = props.options.filter((option) => option.showWhen())

  if (visibleOptions.length < 1) {
    return null
  }
  return (
    <Card.Content>
      <List verticalAlign="middle" selection>
        {visibleOptions.map((option) =>
          option.action ? (
            <TaskAction key={option.id} option={option} />
          ) : (
            <TaskModal key={option.id} option={option} {...props} />
          )
        )}
      </List>
    </Card.Content>
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

interface TaskModalProps extends TaskActionProps {
  option: TaskOption
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
