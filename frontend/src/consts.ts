export const URLS = {
  PERSON: {
    CREATE: '/clerk/parties/create/',
  },
} as const

export const STAGES = {
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

export const CASE_TYPES = {
  REPAIRS: 'Repairs',
  BONDS: 'Bonds',
  EVICTION: 'Eviction',
} as const

export const GROUPS = {
  PARALEGAL: 'Paralegal',
  ADMIN: 'Admin',
  COORDINATOR: 'Coordinator',
  LAWYER: 'Lawyer',
} as const
