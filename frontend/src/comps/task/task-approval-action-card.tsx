import {
  TaskApprovalUpdate,
  TaskStatusUpdate,
  useUpdateTaskApprovalMutation,
  useUpdateTaskStatusMutation,
} from 'api'
import { enqueueSnackbar } from 'notistack'
import React from 'react'
import { Card } from 'semantic-ui-react'
import { TaskDetailProps, TaskStatus } from 'types/task'
import { getAPIErrorMessage } from 'utils'
import { TaskActionCardContent, TaskOption } from './task-action-card'

export interface ModalProps extends TaskApprovalActionProps {
  onClose: () => void
  open: boolean
}

interface TaskApprovalActionProps extends Omit<TaskDetailProps, 'choices'> {
  status: TaskStatus
}

export const TaskApprovalActionCard = ({
  task,
  setTask,
  status,
  user,
}: TaskApprovalActionProps) => {
  const [updateTaskApproval] = useUpdateTaskApprovalMutation()

  const updateApprovalHandler = (values: TaskApprovalUpdate) => {
    updateTaskApproval({
      id: task.id,
      taskApprovalUpdate: values,
    })
      .unwrap()
      .then((task) => {
        setTask(task)
        enqueueSnackbar('Updated task approval', { variant: 'success' })
      })
      .catch((e) => {
        enqueueSnackbar(
          getAPIErrorMessage(e, 'Failed to update task approval'),
          {
            variant: 'error',
          }
        )
      })
  }

  const options: TaskOption[] = [
    {
      id: 'reopen',
      icon: 'undo',
      text: 'Reopen the task',
      showWhen: () => user.is_paralegal_or_better && !task.is_open,
      action: () =>
        updateApprovalHandler({
          status: status.stopped,
          requesting_task: { is_approved: false },
        }),
    },
    {
      id: 'approve',
      icon: 'check',
      text: 'Approve the request',
      showWhen: () => task.is_open,
      action: () =>
        updateApprovalHandler({
          status: status.finished,
          requesting_task: { is_approved: true },
        }),
    },
    {
      id: 'deny',
      icon: 'close',
      text: 'Deny the request',
      showWhen: () => task.is_open,
      action: () =>
        updateApprovalHandler({
          status: status.finished,
          requesting_task: { is_approved: false },
        }),
    },
  ]

  return (
    <Card fluid>
      <Card.Content header="Task actions" />
      <TaskActionCardContent options={options} />
    </Card>
  )
}
