import { Task, TaskStatus, TaskType } from 'api'
import { SetModel, UpdateModel, UserInfo } from 'types/global'

export interface TaskTypesRequest {
  APPROVAL: string
}

export type TaskTypesWithoutRequestTypes = {
  [key in Exclude<TaskType, keyof TaskTypesRequest>]: string
}

export type TaskTypes = {
  [key in TaskType]: string
}

export type TaskStatuses = {
  [key in TaskStatus]: string
}

export interface TaskDetailProps {
  task: Task
  setTask: SetModel<Task>
  update: UpdateModel<Task>
  user: UserInfo
}
