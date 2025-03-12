import { Issue, IssueEventType, IssueStage, IssueTopic } from 'api'

export interface CaseFormServiceChoices {
  category: string[][]
  type_DISCRETE: string[][]
  type_ONGOING: string[][]
}

export type CaseTopics = {
  [key in IssueTopic]: string
}

export type CaseStages = {
  [key in IssueStage]: string
}

export type CaseEventTypes = {
  [key in IssueEventType]: string
}

export interface CaseFormChoices {
  service: CaseFormServiceChoices
}

export interface CaseDetailFormProps {
  choices: CaseFormChoices
  issue: Issue
  onCancel: () => void
}
