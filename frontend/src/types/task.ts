import { Task } from 'api'
import { SetModel, UpdateModel, UserInfo } from 'types/global'

export interface TaskStatus {
  cancelled: string
  finished: string
  started: string
  stopped: string
}

export interface TaskDetailChoices {
  event_type: [string, string][]
  status: [string, string][]
  type: [string, string][]
}

export interface TaskDetailProps {
  choices: TaskDetailChoices
  task: Task
  setTask: SetModel<Task>
  update: UpdateModel<Task>
  user: UserInfo
}
