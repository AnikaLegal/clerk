import { TaskList } from 'api'
import React from 'react'
import { SemanticCOLORS, Table } from 'semantic-ui-react'

export const getApprovalTextAndColor = (
  task: TaskList
): [string, SemanticCOLORS] => {
  if (task.is_approval_required) {
    if (task.is_approved) {
      return ['Approved', 'green']
    } else if (task.is_approval_pending) {
      return ['Pending', 'yellow']
    } else {
      return ['Required', 'orange']
    }
  }
  return ['-', null]
}

export interface TaskApprovalTableCellProps {
  task: TaskList
}
export const TaskApprovalTableCell = ({ task }: TaskApprovalTableCellProps) => {
  const [text, color] = getApprovalTextAndColor(task)
  return (
    <Table.Cell className={color} textAlign="center">
      {text}
    </Table.Cell>
  )
}
