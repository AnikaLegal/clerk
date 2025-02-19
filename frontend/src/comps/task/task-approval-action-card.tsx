import { TaskStatusUpdate } from 'api'
import React from 'react'
import { Card } from 'semantic-ui-react'
import { TaskDetailProps, TaskStatus } from 'types/task'
import { TaskActionCardContent, TaskOption } from './task-action-card'

export interface ModalProps extends TaskApprovalActionProps {
  onClose: () => void
  open: boolean
}

interface TaskApprovalActionProps extends Omit<TaskDetailProps, 'choices'> {
  status: TaskStatus
}

export const TaskApprovalActionCard = ({ task, ...props }: TaskApprovalActionProps) => {
  const updateStatusHandler = (values: TaskStatusUpdate) => {}

  const options: TaskOption[] = [
    {
      id: 'approve',
      icon: 'check',
      text: 'Approve the request',
      showWhen: () => task.is_open,
      action: () => {},
    },
    {
      id: 'deny',
      icon: 'close',
      text: 'Deny the request',
      showWhen: () => task.is_open,
      action: () => {},
    },
  ]

  return (
    <Card fluid>
      <Card.Content header="Task actions" />
      <TaskActionCardContent options={options} task={task} {...props} />
    </Card>
  )
}
