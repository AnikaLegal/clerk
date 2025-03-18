import { Task, TaskList } from 'api'
import React, { ReactNode } from 'react'

export interface TaskAssignedToNodeProps {
  task: Task | TaskList
}
export const TaskAssignedToNode = ({
  task,
}: TaskAssignedToNodeProps): ReactNode => {
  if (task.assigned_to) {
    return <a href={task.assigned_to.url}>{task.assigned_to.full_name}</a>
  }
  if (task.is_suspended) {
    return 'SUSPENDED'
  }
  return '-'
}
