import { Task, TaskList } from 'api'
import React from 'react'
import { SemanticCOLORS, Table } from 'semantic-ui-react'

export const getTaskApprovalText = (task: Task | TaskList): string => {
  if (task.is_approval_required) {
    if (task.is_approved) {
      return 'Approved'
    } else if (task.is_approval_pending) {
      return 'Pending'
    } else {
      return 'Required'
    }
  }
  return '-'
}

export const getTaskApprovalColor = (
  task: Task | TaskList
): SemanticCOLORS | undefined => {
  if (task.is_approval_required) {
    if (task.is_approved) {
      return 'green'
    } else if (task.is_approval_pending) {
      return 'orange'
    } else {
      return 'red'
    }
  }
  return undefined
}

export interface TaskApprovalTableCellProps {
  task: TaskList
}
export const TaskApprovalTableCell = ({ task }: TaskApprovalTableCellProps) => {
  const text = getTaskApprovalText(task)
  const color = getTaskApprovalColor(task)
  return (
    <Table.Cell className={color} textAlign="center">
      {text}
    </Table.Cell>
  )
}
