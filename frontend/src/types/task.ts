import { Task } from 'api'
import { SetModel, UpdateModel, UserInfo } from 'types/global'

export interface TaskDetailChoices {
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
