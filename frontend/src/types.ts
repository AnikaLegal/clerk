import { Issue } from 'api'

export interface UserPermission {
  is_admin: boolean
  is_admin_or_better: boolean
  is_coordinator: boolean
  is_coordinator_or_better: boolean
  is_paralegal: boolean
  is_paralegal_or_better: boolean
}

export interface CaseFormChoices {
  service: {
    category: string[][]
    type_DISCRETE: string[][]
    type_ONGOING: string[][]
  }
}

export interface CaseDetailFormProps {
  choices: CaseFormChoices
  issue: Issue
  onCancel: () => void
}

