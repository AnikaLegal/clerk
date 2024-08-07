import { Task } from 'api'
import { ModelChoices, UserPermission, SetModel, UpdateModel } from 'types/global'

export interface TaskStatus {
  cancel: string
  finish: string
  start: string
  stop: string
}

export interface TaskDetailProps {
  choices: ModelChoices
  perms: UserPermission
  setTask: SetModel<Task>
  task: Task
  update: UpdateModel<Task>
}


