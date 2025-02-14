import { useUpdateTaskStatusMutation, TaskStatusUpdate } from 'api'
import { TextButton } from 'comps/button'
import { CancelTaskModal, RequestApprovalModal } from 'comps/task'
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

interface TaskOption {
  id: string
  icon: SemanticICONS
  text: string
  showWhen: () => boolean
  disableWhen?: () => boolean
  action: () => void
}

export const TaskActionCard = (props: TaskActionProps) => {
  const [updateTaskStatus] = useUpdateTaskStatusMutation()
  const [openCancel, setOpenCancel] = useState(false)
  const [openApprove, setOpenApprove] = useState(false)

  const task = props.task
  const status = props.status
  const user = props.user
  const isApproved =
    user.is_lawyer_or_better || !task.is_approval_required || task.is_approved

  const updateStatusHandler = (values: TaskStatusUpdate) => {
    updateTaskStatus({ id: task.id, taskStatusUpdate: values })
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

  const finishTaskHandler = () => {
    if (isApproved) {
      updateStatusHandler({ status: status.finished })
    } else {
      setOpenApprove(true)
    }
  }

  const cancelTaskHandler = () => {
    if (isApproved) {
      setOpenCancel(true)
    } else {
      setOpenApprove(true)
    }
  }

  const options: TaskOption[] = [
    {
      id: 'reopen',
      icon: 'undo',
      text: 'Reopen the task',
      showWhen: () => user.is_paralegal_or_better && !task.is_open,
      action: () => updateStatusHandler({ status: status.stopped }),
    },
    {
      id: 'start',
      icon: 'play',
      text: 'Start the task',
      showWhen: () =>
        user.is_paralegal_or_better && task.status === status.stopped,
      action: () => updateStatusHandler({ status: status.started }),
    },
    {
      id: 'stop',
      icon: 'stop',
      text: 'Stop the task',
      showWhen: () =>
        user.is_paralegal_or_better && task.status === status.started,
      action: () => updateStatusHandler({ status: status.stopped }),
    },
    {
      id: 'complete',
      icon: 'check',
      text: 'Complete the task',
      showWhen: () => user.is_paralegal_or_better && task.is_open,
      action: () => finishTaskHandler(),
    },
    {
      id: 'cancel',
      icon: 'close',
      text: 'Cancel the task',
      showWhen: () => user.is_paralegal_or_better && task.is_open,
      action: () => cancelTaskHandler(),
    },
  ]

  return (
    <Card fluid>
      <CancelTaskModal
        open={openCancel}
        onClose={() => setOpenCancel(false)}
        {...props}
      />
      <RequestApprovalModal
        open={openApprove}
        onClose={() => setOpenApprove(false)}
        {...props}
      />
      <Card.Content header="Task actions" />
      <TaskActionCardContent options={options} {...props} />
    </Card>
  )
}

interface TaskActionCardContentProps extends TaskActionProps {
  options: TaskOption[]
}
export const TaskActionCardContent = (props: TaskActionCardContentProps) => {
  const options = props.options.filter((option) => option.showWhen())
  if (options.length < 1) {
    return null
  }
  return (
    <Card.Content>
      <List verticalAlign="middle" selection>
        {options.map((option) => (
          <TaskAction key={option.id} option={option} />
        ))}
      </List>
    </Card.Content>
  )
}

export const TaskAction = ({ option }: { option: TaskOption }) => {
  return (
    <List.Item key={option.id}>
      <List.Content>
        <List.Header>
          <TextButton
            icon
            disabled={option.disableWhen && option.disableWhen()}
            onClick={option.action}
          >
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
