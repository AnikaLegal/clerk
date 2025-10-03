import {
  Issue,
  IssueDateHearingType,
  IssueDateType,
  ServiceCategory,
  ServiceTypeDiscrete,
  ServiceTypeOngoing,
} from 'api'

export interface UserPermission {
  is_admin: boolean
  is_admin_or_better: boolean
  is_coordinator: boolean
  is_coordinator_or_better: boolean
  is_paralegal: boolean
  is_paralegal_or_better: boolean
}

export type ServiceCategories = {
  [key in ServiceCategory]: string
}

export type DiscreteServiceTypes = {
  [key in ServiceTypeDiscrete]: string
}

export type OngoingServiceTypes = {
  [key in ServiceTypeOngoing]: string
}

export type CaseDateTypes = {
  [key in IssueDateType]: string
}

export type CaseDateHearingTypes = {
  [key in IssueDateHearingType]: string
}

export interface CaseDetailFormProps {
  issue: Issue
  onCancel: () => void
}
