import { Task, TaskType } from 'api'
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

export interface TaskDetailChoices {
  status: [string, string][]
}

export interface TaskDetailProps {
  choices: TaskDetailChoices
  task: Task
  setTask: SetModel<Task>
  update: UpdateModel<Task>
  user: UserInfo
}
