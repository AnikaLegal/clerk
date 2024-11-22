import { Issue } from 'api'

export interface CaseFormServiceChoices {
  category: string[][]
  type_DISCRETE: string[][]
  type_ONGOING: string[][]
}

export interface CaseFormChoices {
  service: CaseFormServiceChoices
}

export interface CaseDetailFormProps {
  choices: CaseFormChoices
  issue: Issue
  onCancel: () => void
}
