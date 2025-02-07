import { TaskList } from 'api'
import moment from 'moment'
import React from 'react'
import { SemanticCOLORS, Table } from 'semantic-ui-react'

export interface TaskDueDateTableCellProps {
  task: TaskList
}

const getDueDateColor = (task: TaskList): SemanticCOLORS => {
  if (task.is_urgent) {
    return 'red'
  }
  if (task.due_at) {
    const now = moment().startOf('day')
    const due_at = moment(task.due_at, 'DD/MM/YYYY')
    const days = due_at.diff(now, 'days')
    if (days <= 7) {
      if (days >= 3) {
        return 'green'
      } else if (days >= 2) {
        return 'yellow'
      } else if (days >= 1) {
        return 'orange'
      } else {
        return 'red'
      }
    }
  }
  return null
}

export const TaskDueDateTableCell = ({ task }: TaskDueDateTableCellProps) => {
  return (
    <Table.Cell className={getDueDateColor(task)} textAlign="center">
      {task.is_urgent ? (
        <span className="animation-tada">URGENT</span>
      ) : (
        task.due_at || '-'
      )}
    </Table.Cell>
  )
}
