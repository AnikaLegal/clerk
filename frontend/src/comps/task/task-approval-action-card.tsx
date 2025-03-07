import api, { Task, TaskRequestUpdate, useUpdateTaskRequestMutation } from 'api'
import { enqueueSnackbar } from 'notistack'
import React, { useState } from 'react'
import { Card } from 'semantic-ui-react'
import { TaskDetailProps } from 'types/task'
import { getAPIErrorMessage } from 'utils'
import { ApprovalDecision, ApprovalDecisionModal } from './modal'
import { TaskActionCardContent, TaskOption } from './task-action-card'

export interface ModalProps extends TaskApprovalActionProps {
  onClose: () => void
  open: boolean
}

interface TaskApprovalActionProps extends Omit<TaskDetailProps, 'choices'> {}

export const TaskApprovalActionCard = ({
  task,
  user,
  setTask,
  ...props
}: TaskApprovalActionProps) => {
  const [getTask] = api.useLazyGetTaskQuery()
  const [updateTaskRequest] = useUpdateTaskRequestMutation()
  const [openApprovalDecision, setOpenApprovalDecision] = useState(false)
  const [decision, setDecision] = useState<ApprovalDecision>('DECLINED')

  const updateTask = () => {
    getTask({ id: task.id })
      .unwrap()
      .then((task) => {
        setTask(task)
      })
  }

  const updateRequest = (values: TaskRequestUpdate) => {
    return updateTaskRequest({
      id: task.request.from_task_id,
      requestId: task.request.id,
      taskRequestUpdate: values,
    })
      .unwrap()
      .then(() => {
        enqueueSnackbar('Updated task approval', { variant: 'success' })
        updateTask()
      })
      .catch((e) => {
        const mesg = getAPIErrorMessage(e, 'Failed to update task approval')
        enqueueSnackbar(mesg, { variant: 'error' })
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
        updateRequest({
          status: 'PENDING',
          is_approved: false,
        }),
    },
    {
      id: 'approve',
      icon: 'check',
      text: 'Approve the request',
      showWhen: () => task.is_open,
      action: () => showApprovalModal('APPROVED'),
    },
    {
      id: 'decline',
      icon: 'close',
      text: 'Decline the request',
      showWhen: () => task.is_open,
      action: () => showApprovalModal('DECLINED'),
    },
  ]

  return (
    <Card fluid>
      <ApprovalDecisionModal
        task={task}
        setTask={setTask}
        open={openApprovalDecision}
        onClose={() => setOpenApprovalDecision(false)}
        decision={decision}
        updateRequest={updateRequest}
        user={user}
        {...props}
      />
      <Card.Content header="Task actions" />
      <TaskActionCardContent options={options} />
    </Card>
  )
}
