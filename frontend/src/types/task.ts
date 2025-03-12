import {
  Task,
  TaskStatus,
  TaskTriggerRole,
  TaskTriggerTopic,
  TaskType,
} from 'api'
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

export type TaskIsOpen = {
  [key in 'true' | 'false']: string
}

export type TaskTriggerTopics = {
  [key in TaskTriggerTopic]: string
}

export type TaskTriggerRoles = {
  [key in TaskTriggerRole]: string
}

export interface TaskDetailProps {
  task: Task
  setTask: SetModel<Task>
  update: UpdateModel<Task>
  user: UserInfo
}
