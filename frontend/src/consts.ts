import { CaseEventTypes, CaseStages, CaseTopics } from 'types/case'
import {
  TaskIsOpen,
  TaskStatuses,
  TaskTriggerRoles,
  TaskTriggerTopics,
  TaskTypes,
  TaskTypesRequest,
  TaskTypesWithoutRequestTypes,
} from 'types/task'
import {
  DiscreteServiceTypes,
  OngoingServiceTypes,
  ServiceCategories,
} from 'types/case'

export const URLS = {
  PERSON: {
    CREATE: '/clerk/parties/create/',
  },
} as const

export const CASE_STAGES: CaseStages = {
  UNSTARTED: 'Not started',
  CLIENT_AGREEMENT: 'Client agreement',
  ADVICE: 'Drafting advice',
  FORMAL_LETTER: 'Formal letter sent',
  NEGOTIATIONS: 'Negotiations',
  VCAT_CAV: 'VCAT/CAV',
  POST_CASE_INTERVIEW: 'Post-case interview',
  CLOSED: 'Closed',
} as const

export const OUTCOMES = {
  OUT_OF_SCOPE: 'Out of scope',
  CHANGE_OF_SCOPE: 'Change of scope',
  RESOLVED_EARLY: 'Resolved early',
  CHURNED: 'Churned',
  UNKNOWN: 'Unknown',
  SUCCESSFUL: 'Successful',
  UNSUCCESSFUL: 'Unsuccessful',
} as const

export const CASE_TOPICS: CaseTopics = {
  REPAIRS: 'Repairs',
  BONDS: 'Bonds',
  EVICTION_ARREARS: 'Eviction (Arrears)',
} as const

export const CASE_EVENT_TYPES: CaseEventTypes = {
  CREATE: 'Created',
  LAWYER: 'Lawyer assigned',
  PARALEGAL: 'Paralegal assigned',
  STAGE: 'Stage change',
  OPEN: 'Open change',
} as const

export const GROUPS = {
  PARALEGAL: 'Paralegal',
  ADMIN: 'Admin',
  COORDINATOR: 'Coordinator',
  LAWYER: 'Lawyer',
} as const

export const TASK_TRIGGER_TOPICS: TaskTriggerTopics = {
  ANY: 'Any',
  ...CASE_TOPICS,
} as const

export const TASK_TRIGGER_ROLES: TaskTriggerRoles = {
  PARALEGAL: 'Paralegal',
  LAWYER: 'Lawyer',
  COORDINATOR: 'Coordinators',
} as const

export const TASK_TYPES_REQUEST: TaskTypesRequest = {
  APPROVAL: 'Approval request',
} as const

export const TASK_TYPES_WITHOUT_REQUEST_TYPES: TaskTypesWithoutRequestTypes = {
  CHECK: 'Check for conflict/eligibility',
  CONTACT: 'Contact client or other party',
  DRAFT: 'Draft document or advice',
  MANAGE: 'Manage the case file',
  REVIEW: 'Review document or advice',
  SEND: 'Send document or advice',
  OTHER: 'Other',
} as const

export const TASK_TYPES: TaskTypes = {
  ...TASK_TYPES_REQUEST,
  ...TASK_TYPES_WITHOUT_REQUEST_TYPES,
} as const

export const TASK_STATUSES: TaskStatuses = {
  NOT_STARTED: 'Not started',
  IN_PROGRESS: 'In progress',
  DONE: 'Done',
  NOT_DONE: 'Not done',
} as const

export const TASK_IS_OPEN: TaskIsOpen = {
  true: 'Open',
  false: 'Closed',
} as const

export const SERVICE_CATEGORIES: ServiceCategories = {
  DISCRETE: 'Discrete service',
  ONGOING: 'Ongoing service',
} as const

export const DISCRETE_SERVICE_TYPES: DiscreteServiceTypes = {
  LEGAL_ADVICE: 'Legal advice',
  LEGAL_TASK: 'Legal task',
  GENERAL_INFORMATION: 'Information',
  GENERAL_REFERRAL_SIMPLE: 'Referral (Simple)',
  GENERAL_REFERRAL_FACILITATED: 'Referral (Facilitated)',
} as const

export const ONGOING_SERVICE_TYPES: OngoingServiceTypes = {
  LEGAL_SUPPORT: 'Legal support',
  REPRESENTATION_COURT_TRIBUNAL: 'Court or tribunal representation',
  REPRESENTATION_OTHER: 'Other representation',
} as const
