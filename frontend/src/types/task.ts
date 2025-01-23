import { Task } from 'api'
import { ModelChoices, UserInfo, SetModel, UpdateModel } from 'types/global'

export interface TaskStatus {
  cancelled: string
  finished: string
  started: string
  stopped: string
}

export interface TaskDetailProps {
  choices: ModelChoices
  task: Task
  setTask: SetModel<Task>
  update: UpdateModel<Task>
  user: UserInfo
}


