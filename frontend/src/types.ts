export type TextChoiceField = {
  display: string
  value: string
  choices: string[]
}

export type CreatePerson = {
  full_name: string
  email: string
  address: string
  phone_number: string
  support_contact_preferences: string
}

export type Person = {
  id: number
  full_name: string
  email: string
  address: string
  phone_number: string
  url: string
  support_contact_preferences: TextChoiceField
}

export type User = {
  id: number
  first_name: string
  last_name: string
  full_name: string
  is_active: boolean
  email: string
  case_capacity: number
  is_intern: boolean
  is_superuser: boolean
  created_at: string
  groups: string[]
  url: string
  is_admin_or_better: boolean
  is_coordinator_or_better: boolean
  is_paralegal_or_better: boolean
  is_admin: boolean
  is_coordinator: boolean
  is_paralegal: boolean
  is_ms_account_set_up: boolean
}

export type AccountDetail = User & {
  issue_set: IssueDetail[]
  lawyer_issues: IssueDetail[]
  performance_notes: any[]
  ms_account_created_at: string | null
  university: TextChoiceField
}

export type Client = {
  id: string
  first_name: string
  last_name: string
  email: string
  date_of_birth: string
  phone_number: string
  employment_status: string
  weekly_income: number
  gender: string
  centrelink_support: boolean
  eligibility_notes: string
  requires_interpreter: boolean
  primary_language_non_english: boolean
  primary_language: string
  is_aboriginal_or_torres_strait_islander: boolean
  rental_circumstances: string
  number_of_dependents: number
  eligibility_circumstances: string[]
  referrer_type: string
  referrer: string
  age: number
  full_name: string
  notes: string
  url: string
}

export type ClientDetail = Client & {
  issue_set: IssueDetail[]
  referrer_type: TextChoiceField
  call_times: TextChoiceField
  employment_status: TextChoiceField
  eligibility_circumstances: TextChoiceField
  rental_circumstances: TextChoiceField
}

export type Issue = {
  id: string // UUID
  topic: string
  topic_display: string
  stage_display: string
  stage: string
  outcome: string
  outcome_display: string
  outcome_notes: string
  provided_legal_services: boolean
  fileref: string
  paralegal: User | null
  lawyer: User | null
  is_open: boolean
  is_sharepoint_set_up: boolean
  actionstep_id: number
  created_at: string
  url: string
}

export type IssueDetail = Issue & {
  client: ClientDetail
  support_worker: Person | null
}

type NoteType =
  | 'PARALEGAL'
  | 'EVENT'
  | 'ELIGIBILITY_CHECK_SUCCESS'
  | 'ELIGIBILITY_CHECK_FAILURE'
  | 'CONFLICT_CHECK_SUCCESS'
  | 'CONFLICT_CHECK_FAILURE'
  | 'REVIEW'
  | 'PERFORMANCE'
  | 'EMAIL'

export type IssueNote = {
  id: number
  creator: User
  note_type: NoteType
  text: string
  text_display: string
  created_at: any
  event: any
  reviewee: User | void
}
