import { useUpdateTaskStatusMutation, TaskStatusUpdate } from 'api'
import { TextButton } from 'comps/button'
import { CancelTaskModal, RequestApprovalModal } from 'comps/task'
import { enqueueSnackbar } from 'notistack'
import React, { useState } from 'react'
import { Card, Icon, List, SemanticICONS } from 'semantic-ui-react'
import { TaskDetailProps } from 'types/task'
import { getAPIErrorMessage } from 'utils'

interface TaskActionProps extends TaskDetailProps {}

export interface ModalProps extends TaskActionProps {
  onClose: () => void
  open: boolean
}

export interface TaskOption {
  id: string
  icon: SemanticICONS
  text: string
  showWhen: () => boolean
  disableWhen?: () => boolean
  action: () => void
}

export const TaskActionCard = (props: TaskActionProps) => {
  const [updateTaskStatus] = useUpdateTaskStatusMutation()
  const [openCancelTask, setOpenCancelTask] = useState(false)
  const [openRequestApproval, setOpenRequestApproval] = useState(false)

  const task = props.task
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
      updateStatusHandler({ status: 'DONE' })
    } else {
      setOpenRequestApproval(true)
    }
  }

  const cancelTaskHandler = () => {
    setOpenCancelTask(true)
  }

  const options: TaskOption[] = [
    {
      id: 'reopen',
      icon: 'undo',
      text: 'Reopen the task',
      showWhen: () => user.is_paralegal_or_better && !task.is_open,
      action: () => updateStatusHandler({ status: 'NOT_STARTED' }),
    },
    {
      id: 'start',
      icon: 'play',
      text: 'Start the task',
      showWhen: () =>
        user.is_paralegal_or_better && task.status == 'NOT_STARTED',
      action: () => updateStatusHandler({ status: 'IN_PROGRESS' }),
    },
    {
      id: 'stop',
      icon: 'stop',
      text: 'Stop the task',
      showWhen: () =>
        user.is_paralegal_or_better && task.status == 'IN_PROGRESS',
      action: () => updateStatusHandler({ status: 'NOT_STARTED' }),
    },
    {
      id: 'complete',
      icon: 'check',
      text: 'Complete the task',
      showWhen: () => user.is_paralegal_or_better && task.is_open,
      disableWhen: () => task.is_approval_required && task.is_approval_pending,
      action: () => finishTaskHandler(),
    },
    {
      id: 'cancel',
      icon: 'close',
      text: 'Cancel the task',
      showWhen: () => user.is_paralegal_or_better && task.is_open,
      disableWhen: () => task.is_approval_required && task.is_approval_pending,
      action: () => cancelTaskHandler(),
    },
  ]

  return (
    <Card fluid>
      <CancelTaskModal
        open={openCancelTask}
        onClose={() => setOpenCancelTask(false)}
        {...props}
      />
      <RequestApprovalModal
        open={openRequestApproval}
        onClose={() => setOpenRequestApproval(false)}
        {...props}
      />
      <Card.Content header="Task actions" />
      <TaskActionCardContent options={options} />
    </Card>
  )
}

interface TaskActionCardContentProps {
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
