import { TaskApprovalUpdate, useUpdateTaskApprovalMutation } from 'api'
import { enqueueSnackbar } from 'notistack'
import React, { useState } from 'react'
import { Card } from 'semantic-ui-react'
import { TaskDetailProps, TaskStatus } from 'types/task'
import { getAPIErrorMessage } from 'utils'
import { ApprovalDecision, ApprovalDecisionModal } from './modal'
import { TaskActionCardContent, TaskOption } from './task-action-card'

export interface ModalProps extends TaskApprovalActionProps {
  onClose: () => void
  open: boolean
}

interface TaskApprovalActionProps extends Omit<TaskDetailProps, 'choices'> {
  status: TaskStatus
}

export const TaskApprovalActionCard = (props: TaskApprovalActionProps) => {
  const [updateTaskApproval] = useUpdateTaskApprovalMutation()
  const [decision, setDecision] = useState<ApprovalDecision>(
    ApprovalDecision.DECLINED
  )
  const [openApprovalDecision, setOpenApprovalDecision] = useState(false)

  const task = props.task
  const status = props.status
  const user = props.user

  const updateApprovalHandler = (values: TaskApprovalUpdate) => {
    updateTaskApproval({
      id: task.id,
      taskApprovalUpdate: values,
    })
      .unwrap()
      .then((task) => {
        props.setTask(task)
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

  const showApprovalModal = (decision: ApprovalDecision) => {
    setDecision(decision)
    setOpenApprovalDecision(true)
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
          requesting_task: { is_approved: false, is_approval_pending: true },
        }),
    },
    {
      id: 'approve',
      icon: 'check',
      text: 'Approve the request',
      showWhen: () => task.is_open,
      action: () => showApprovalModal(ApprovalDecision.APPROVED),
    },
    {
      id: 'decline',
      icon: 'close',
      text: 'Decline the request',
      showWhen: () => task.is_open,
      action: () => showApprovalModal(ApprovalDecision.DECLINED),
    },
  ]

  return (
    <Card fluid>
      <ApprovalDecisionModal
        open={openApprovalDecision}
        onClose={() => setOpenApprovalDecision(false)}
        decision={decision}
        {...props}
      />
      <Card.Content header="Task actions" />
      <TaskActionCardContent options={options} />
    </Card>
  )
}
