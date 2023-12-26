import { baseApi as api } from './baseApi'
const injectedRtkApi = api.injectEndpoints({
  endpoints: (build) => ({
    getCases: build.query<GetCasesApiResponse, GetCasesApiArg>({
      query: (queryArg) => ({
        url: `/clerk/api/case/`,
        params: {
          page: queryArg.page,
          search: queryArg.search,
          topic: queryArg.topic,
          stage: queryArg.stage,
          outcome: queryArg.outcome,
          is_open: queryArg.isOpen,
          paralegal: queryArg.paralegal,
          lawyer: queryArg.lawyer,
        },
      }),
    }),
    getCase: build.query<GetCaseApiResponse, GetCaseApiArg>({
      query: (queryArg) => ({ url: `/clerk/api/case/${queryArg.id}/` }),
    }),
    updateCase: build.mutation<UpdateCaseApiResponse, UpdateCaseApiArg>({
      query: (queryArg) => ({
        url: `/clerk/api/case/${queryArg.id}/`,
        method: 'PATCH',
        body: queryArg.issueUpdate,
      }),
    }),
    createCaseNote: build.mutation<
      CreateCaseNoteApiResponse,
      CreateCaseNoteApiArg
    >({
      query: (queryArg) => ({
        url: `/clerk/api/case/${queryArg.id}/note/`,
        method: 'POST',
        body: queryArg.issueNoteCreate,
      }),
    }),
    getCaseDocuments: build.query<
      GetCaseDocumentsApiResponse,
      GetCaseDocumentsApiArg
    >({
      query: (queryArg) => ({ url: `/clerk/api/case/${queryArg.id}/docs/` }),
    }),
    getPeople: build.query<GetPeopleApiResponse, GetPeopleApiArg>({
      query: () => ({ url: `/clerk/api/person/` }),
    }),
    createPerson: build.mutation<CreatePersonApiResponse, CreatePersonApiArg>({
      query: (queryArg) => ({
        url: `/clerk/api/person/`,
        method: 'POST',
        body: queryArg.personCreate,
      }),
    }),
    searchPeople: build.query<SearchPeopleApiResponse, SearchPeopleApiArg>({
      query: (queryArg) => ({
        url: `/clerk/api/person/search/`,
        params: { query: queryArg.query },
      }),
    }),
    getPerson: build.query<GetPersonApiResponse, GetPersonApiArg>({
      query: (queryArg) => ({ url: `/clerk/api/person/${queryArg.id}/` }),
    }),
    updatePerson: build.mutation<UpdatePersonApiResponse, UpdatePersonApiArg>({
      query: (queryArg) => ({
        url: `/clerk/api/person/${queryArg.id}/`,
        method: 'PUT',
        body: queryArg.personCreate,
      }),
    }),
    deletePerson: build.mutation<DeletePersonApiResponse, DeletePersonApiArg>({
      query: (queryArg) => ({
        url: `/clerk/api/person/${queryArg.id}/`,
        method: 'DELETE',
      }),
    }),
    getTenancy: build.query<GetTenancyApiResponse, GetTenancyApiArg>({
      query: (queryArg) => ({ url: `/clerk/api/tenancy/${queryArg.id}/` }),
    }),
    updateTenancy: build.mutation<
      UpdateTenancyApiResponse,
      UpdateTenancyApiArg
    >({
      query: (queryArg) => ({
        url: `/clerk/api/tenancy/${queryArg.id}/`,
        method: 'PATCH',
        body: queryArg.tenancyCreate,
      }),
    }),
    updateClient: build.mutation<UpdateClientApiResponse, UpdateClientApiArg>({
      query: (queryArg) => ({
        url: `/clerk/api/client/${queryArg.id}/`,
        method: 'PATCH',
        body: queryArg.clientCreate,
      }),
    }),
    getUsers: build.query<GetUsersApiResponse, GetUsersApiArg>({
      query: (queryArg) => ({
        url: `/clerk/api/account/`,
        params: { name: queryArg.name, group: queryArg.group },
      }),
    }),
    createUser: build.mutation<CreateUserApiResponse, CreateUserApiArg>({
      query: (queryArg) => ({
        url: `/clerk/api/account/`,
        method: 'POST',
        body: queryArg.userCreate,
      }),
    }),
    updateUser: build.mutation<UpdateUserApiResponse, UpdateUserApiArg>({
      query: (queryArg) => ({
        url: `/clerk/api/account/${queryArg.id}/`,
        method: 'PATCH',
        body: queryArg.userCreate,
      }),
    }),
    getUserAccountPermissions: build.query<
      GetUserAccountPermissionsApiResponse,
      GetUserAccountPermissionsApiArg
    >({
      query: (queryArg) => ({
        url: `/clerk/api/account/${queryArg.id}/perms/`,
      }),
    }),
    resyncUserAccountPermissions: build.mutation<
      ResyncUserAccountPermissionsApiResponse,
      ResyncUserAccountPermissionsApiArg
    >({
      query: (queryArg) => ({
        url: `/clerk/api/account/${queryArg.id}/perms-resync/`,
        method: 'POST',
      }),
    }),
    promoteUserAccountPermissions: build.mutation<
      PromoteUserAccountPermissionsApiResponse,
      PromoteUserAccountPermissionsApiArg
    >({
      query: (queryArg) => ({
        url: `/clerk/api/account/${queryArg.id}/perms-promote/`,
        method: 'POST',
      }),
    }),
    demoteUserAccountPermissions: build.mutation<
      DemoteUserAccountPermissionsApiResponse,
      DemoteUserAccountPermissionsApiArg
    >({
      query: (queryArg) => ({
        url: `/clerk/api/account/${queryArg.id}/perms-demote/`,
        method: 'POST',
      }),
    }),
    getEmailTemplates: build.query<
      GetEmailTemplatesApiResponse,
      GetEmailTemplatesApiArg
    >({
      query: (queryArg) => ({
        url: `/clerk/api/template-email/`,
        params: { name: queryArg.name, topic: queryArg.topic },
      }),
    }),
    createEmailTemplate: build.mutation<
      CreateEmailTemplateApiResponse,
      CreateEmailTemplateApiArg
    >({
      query: (queryArg) => ({
        url: `/clerk/api/template-email/`,
        method: 'POST',
        body: queryArg.emailTemplateCreate,
      }),
    }),
    getEmailTemplate: build.query<
      GetEmailTemplateApiResponse,
      GetEmailTemplateApiArg
    >({
      query: (queryArg) => ({
        url: `/clerk/api/template-email/${queryArg.id}/`,
      }),
    }),
    updateEmailTemplate: build.mutation<
      UpdateEmailTemplateApiResponse,
      UpdateEmailTemplateApiArg
    >({
      query: (queryArg) => ({
        url: `/clerk/api/template-email/${queryArg.id}/`,
        method: 'PATCH',
        body: queryArg.emailTemplateCreate,
      }),
    }),
    deleteEmailTemplate: build.mutation<
      DeleteEmailTemplateApiResponse,
      DeleteEmailTemplateApiArg
    >({
      query: (queryArg) => ({
        url: `/clerk/api/template-email/${queryArg.id}/`,
        method: 'DELETE',
      }),
    }),
    getNotificationTemplates: build.query<
      GetNotificationTemplatesApiResponse,
      GetNotificationTemplatesApiArg
    >({
      query: (queryArg) => ({
        url: `/clerk/api/template-notify/`,
        params: { name: queryArg.name, topic: queryArg.topic },
      }),
    }),
    createNotificationTemplate: build.mutation<
      CreateNotificationTemplateApiResponse,
      CreateNotificationTemplateApiArg
    >({
      query: (queryArg) => ({
        url: `/clerk/api/template-notify/`,
        method: 'POST',
        body: queryArg.notificationTemplateCreate,
      }),
    }),
    getNotificationTemplate: build.query<
      GetNotificationTemplateApiResponse,
      GetNotificationTemplateApiArg
    >({
      query: (queryArg) => ({
        url: `/clerk/api/template-notify/${queryArg.id}/`,
      }),
    }),
    updateNotificationTemplate: build.mutation<
      UpdateNotificationTemplateApiResponse,
      UpdateNotificationTemplateApiArg
    >({
      query: (queryArg) => ({
        url: `/clerk/api/template-notify/${queryArg.id}/`,
        method: 'PATCH',
        body: queryArg.notificationTemplateCreate,
      }),
    }),
    deleteNotificationTemplate: build.mutation<
      DeleteNotificationTemplateApiResponse,
      DeleteNotificationTemplateApiArg
    >({
      query: (queryArg) => ({
        url: `/clerk/api/template-notify/${queryArg.id}/`,
        method: 'DELETE',
      }),
    }),
    getDocumentTemplates: build.query<
      GetDocumentTemplatesApiResponse,
      GetDocumentTemplatesApiArg
    >({
      query: (queryArg) => ({
        url: `/clerk/api/template-doc/`,
        params: { name: queryArg.name, topic: queryArg.topic },
      }),
    }),
    createDocumentTemplate: build.mutation<
      CreateDocumentTemplateApiResponse,
      CreateDocumentTemplateApiArg
    >({
      query: (queryArg) => ({
        url: `/clerk/api/template-doc/`,
        method: 'POST',
        body: queryArg.documentTemplateCreate,
      }),
    }),
    deleteDocumentTemplate: build.mutation<
      DeleteDocumentTemplateApiResponse,
      DeleteDocumentTemplateApiArg
    >({
      query: (queryArg) => ({
        url: `/clerk/api/template-doc/${queryArg.id}/`,
        method: 'DELETE',
      }),
    }),
  }),
  overrideExisting: false,
})
export { injectedRtkApi as generatedApi }
export type GetCasesApiResponse = /** status 200 Successful response. */ {
  current: number
  next: number | null
  prev: number | null
  page_count: number
  item_count: number
  results: Issue[]
}
export type GetCasesApiArg = {
  page?: number
  search?: string
  topic?: string
  stage?: string
  outcome?: string
  isOpen?: string
  paralegal?: string
  lawyer?: string
}
export type GetCaseApiResponse = /** status 200 Successful response. */ {
  issue: Issue
  tenancy: Tenancy
  notes: IssueNote[]
}
export type GetCaseApiArg = {
  /** Entity ID */
  id: string
}
export type UpdateCaseApiResponse = /** status 200 Successful response. */ Issue
export type UpdateCaseApiArg = {
  /** Entity ID */
  id: string
  /** Successful response. */
  issueUpdate: IssueUpdate
}
export type CreateCaseNoteApiResponse =
  /** status 200 Successful response. */ IssueNote
export type CreateCaseNoteApiArg = {
  /** Entity ID */
  id: string
  /** Successful response. */
  issueNoteCreate: IssueNoteCreate
}
export type GetCaseDocumentsApiResponse =
  /** status 200 Successful response. */ {
    sharepoint_url: string
    documents: string[][]
  }
export type GetCaseDocumentsApiArg = {
  /** Entity ID */
  id: string
}
export type GetPeopleApiResponse =
  /** status 200 Successful response. */ Person[]
export type GetPeopleApiArg = void
export type CreatePersonApiResponse =
  /** status 201 Successful response. */ Person
export type CreatePersonApiArg = {
  personCreate: PersonCreate
}
export type SearchPeopleApiResponse =
  /** status 200 Successful response. */ Person[]
export type SearchPeopleApiArg = {
  query: string
}
export type GetPersonApiResponse = /** status 200 Successful response. */ Person
export type GetPersonApiArg = {
  /** Entity ID */
  id: number
}
export type UpdatePersonApiResponse =
  /** status 200 Successful response. */ Person
export type UpdatePersonApiArg = {
  /** Entity ID */
  id: number
  /** Successful response. */
  personCreate: PersonCreate
}
export type DeletePersonApiResponse =
  /** status 204 The specific resource was deleted successfully */ void
export type DeletePersonApiArg = {
  /** Entity ID */
  id: number
}
export type GetTenancyApiResponse =
  /** status 200 Successful response. */ Tenancy
export type GetTenancyApiArg = {
  /** Entity ID */
  id: number
}
export type UpdateTenancyApiResponse =
  /** status 200 Successful response. */ Tenancy
export type UpdateTenancyApiArg = {
  /** Entity ID */
  id: number
  /** Successful response. */
  tenancyCreate: TenancyCreate
}
export type UpdateClientApiResponse =
  /** status 200 Successful response. */ Client
export type UpdateClientApiArg = {
  /** Entity ID */
  id: string
  /** Successful response. */
  clientCreate: ClientCreate
}
export type GetUsersApiResponse = /** status 200 Successful response. */ User[]
export type GetUsersApiArg = {
  name?: string
  group?: string
}
export type CreateUserApiResponse = /** status 201 Successful response. */ User
export type CreateUserApiArg = {
  userCreate: UserCreate
}
export type UpdateUserApiResponse = /** status 200 Successful response. */ User
export type UpdateUserApiArg = {
  /** Entity ID */
  id: number
  /** Successful response. */
  userCreate: UserCreate
}
export type GetUserAccountPermissionsApiResponse =
  /** status 200 Successful response. */ MicrosoftUserPermissions
export type GetUserAccountPermissionsApiArg = {
  /** Entity ID */
  id: number
}
export type ResyncUserAccountPermissionsApiResponse =
  /** status 201 Successful response. */ {
    account: User
    permissions: MicrosoftUserPermissions
  }
export type ResyncUserAccountPermissionsApiArg = {
  /** Entity ID */
  id: number
}
export type PromoteUserAccountPermissionsApiResponse =
  /** status 201 Successful response. */ {
    account: User
    permissions: MicrosoftUserPermissions
  }
export type PromoteUserAccountPermissionsApiArg = {
  /** Entity ID */
  id: number
}
export type DemoteUserAccountPermissionsApiResponse =
  /** status 201 Successful response. */ {
    account: User
    permissions: MicrosoftUserPermissions
  }
export type DemoteUserAccountPermissionsApiArg = {
  /** Entity ID */
  id: number
}
export type GetEmailTemplatesApiResponse =
  /** status 200 Successful response. */ EmailTemplate[]
export type GetEmailTemplatesApiArg = {
  name?: string
  topic?: string
}
export type CreateEmailTemplateApiResponse =
  /** status 201 Successful response. */ EmailTemplate
export type CreateEmailTemplateApiArg = {
  emailTemplateCreate: EmailTemplateCreate
}
export type GetEmailTemplateApiResponse =
  /** status 200 Successful response. */ EmailTemplate
export type GetEmailTemplateApiArg = {
  /** Entity ID */
  id: number
}
export type UpdateEmailTemplateApiResponse =
  /** status 200 Successful response. */ EmailTemplate
export type UpdateEmailTemplateApiArg = {
  /** Entity ID */
  id: number
  /** Successful response. */
  emailTemplateCreate: EmailTemplateCreate
}
export type DeleteEmailTemplateApiResponse =
  /** status 204 The specific resource was deleted successfully */ void
export type DeleteEmailTemplateApiArg = {
  /** Entity ID */
  id: number
}
export type GetNotificationTemplatesApiResponse =
  /** status 200 Successful response. */ NotificationTemplate[]
export type GetNotificationTemplatesApiArg = {
  name?: string
  topic?: string
}
export type CreateNotificationTemplateApiResponse =
  /** status 201 Successful response. */ NotificationTemplate
export type CreateNotificationTemplateApiArg = {
  notificationTemplateCreate: NotificationTemplateCreate
}
export type GetNotificationTemplateApiResponse =
  /** status 200 Successful response. */ NotificationTemplate
export type GetNotificationTemplateApiArg = {
  /** Entity ID */
  id: number
}
export type UpdateNotificationTemplateApiResponse =
  /** status 200 Successful response. */ NotificationTemplate
export type UpdateNotificationTemplateApiArg = {
  /** Entity ID */
  id: number
  /** Successful response. */
  notificationTemplateCreate: NotificationTemplateCreate
}
export type DeleteNotificationTemplateApiResponse =
  /** status 204 The specific resource was deleted successfully */ void
export type DeleteNotificationTemplateApiArg = {
  /** Entity ID */
  id: number
}
export type GetDocumentTemplatesApiResponse =
  /** status 200 Successful response. */ DocumentTemplate[]
export type GetDocumentTemplatesApiArg = {
  name?: string
  topic?: string
}
export type CreateDocumentTemplateApiResponse =
  /** status 201 The specific resource was deleted successfully */ void
export type CreateDocumentTemplateApiArg = {
  documentTemplateCreate: DocumentTemplateCreate
}
export type DeleteDocumentTemplateApiResponse =
  /** status 204 The specific resource was deleted successfully */ void
export type DeleteDocumentTemplateApiArg = {
  /** Entity ID */
  id: number
}
export type IssueBase = {
  topic: string
  stage: string
  outcome: string | null
  outcome_notes: string
  provided_legal_services: boolean
  is_open: boolean
}
export type UserCreate = {
  first_name: string
  last_name: string
  email: string
  username: string
}
export type User = UserCreate & {
  id: number
  case_capacity: number
  is_intern: boolean
  is_active: boolean
  is_superuser: boolean
  full_name: string
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
  ms_account_created_at: string | null
}
export type ClientBase = {
  first_name: string
  last_name: string
  email: string
  phone_number: string
  weekly_income: number | null
  gender: string | null
  centrelink_support: boolean
  eligibility_notes: string
  requires_interpreter: boolean
  primary_language_non_english: boolean
  primary_language: string
  is_aboriginal_or_torres_strait_islander: boolean
  number_of_dependents: number | null
  referrer: string
  notes: string
  date_of_birth: string | null
}
export type TextChoiceField = {
  display: string
  value: string
  choices: string[][]
}
export type TextChoiceListField = {
  display: string
  value: string[]
  choices: string[][]
}
export type Client = ClientBase & {
  id: string
  url: string
  age: number
  full_name: string
  referrer_type: TextChoiceField
  call_times: TextChoiceListField
  employment_status: TextChoiceListField
  eligibility_circumstances: TextChoiceListField
  rental_circumstances: TextChoiceField
}
export type PersonBase = {
  full_name: string
  email: string
  address: string
  phone_number: string
}
export type Person = PersonBase & {
  id: number
  url: string
  support_contact_preferences: TextChoiceField
}
export type Issue = IssueBase & {
  id: string
  topic_display: string
  stage_display: string
  outcome_display: string | null
  fileref: string
  is_sharepoint_set_up: boolean
  paralegal: User
  lawyer: User
  client: Client
  support_worker: Person
  actionstep_id: number | null
  created_at: string
  url: string
  answers: {
    [key: string]: string
  }
  is_conflict_check: boolean | null
  is_eligibility_check: boolean | null
  next_review: string | null
}
export type TenancyBase = {
  address: string
  suburb: string | null
  postcode: string | null
  started: string | null
}
export type Tenancy = TenancyBase & {
  id: number
  url: string
  is_on_lease: TextChoiceField
  landlord: Person
  agent: Person
  client: Client
}
export type IssueNoteBase = {
  note_type: string
  text: string
  issue: string
  event: string | null
}
export type IssueNote = IssueNoteBase & {
  id: number
  creator: User
  text_display: string
  created_at: string
  reviewee: User
}
export type Error = {
  detail?: string | object | (string | object | any)[]
  nonFieldErrors?: string[]
}
export type IssueUpdate = IssueBase & {
  paralegal_id: User
  lawyer_id: User
  support_worker_id: Person
}
export type IssueNoteCreate = IssueNoteBase & {
  creator_id: number
}
export type PersonCreate = PersonBase & {
  support_contact_preferences: string
}
export type TenancyCreate = TenancyBase & {
  is_on_lease: string
  landlord_id?: number | null
  agent_id?: number | null
}
export type ClientCreate = ClientBase & {
  referrer_type: string
  call_times: string[]
  employment_status: string[]
  eligibility_circumstances: string[]
  rental_circumstances: string
}
export type MicrosoftUserPermissions = {
  has_coordinator_perms: boolean
  paralegal_perm_issues: Issue[]
  paralegal_perm_missing_issues: Issue[]
}
export type EmailTemplateCreate = {
  name: string
  topic: string
  subject: string
  text: string
}
export type EmailTemplate = EmailTemplateCreate & {
  id: number
  url: string
  created_at: string
}
export type NotificationTemplateBase = {
  name: string
  topic: string
  event_stage: string
  raw_text: string
  message_text: string
}
export type NotificationTemplate = NotificationTemplateBase & {
  id: number
  url: string
  created_at: string
  event: TextChoiceField
  channel: TextChoiceField
  target: TextChoiceField
}
export type NotificationTemplateCreate = NotificationTemplateBase & {
  event: string
  channel: string
  target: string
}
export type DocumentTemplate = {
  id: string
  name: string
  topic: string
  url: string
  created_at: string
  modified_at: string
}
export type DocumentTemplateCreate = {
  topic: string
  files: Blob[]
}
export const {
  useGetCasesQuery,
  useGetCaseQuery,
  useUpdateCaseMutation,
  useCreateCaseNoteMutation,
  useGetCaseDocumentsQuery,
  useGetPeopleQuery,
  useCreatePersonMutation,
  useSearchPeopleQuery,
  useGetPersonQuery,
  useUpdatePersonMutation,
  useDeletePersonMutation,
  useGetTenancyQuery,
  useUpdateTenancyMutation,
  useUpdateClientMutation,
  useGetUsersQuery,
  useCreateUserMutation,
  useUpdateUserMutation,
  useGetUserAccountPermissionsQuery,
  useResyncUserAccountPermissionsMutation,
  usePromoteUserAccountPermissionsMutation,
  useDemoteUserAccountPermissionsMutation,
  useGetEmailTemplatesQuery,
  useCreateEmailTemplateMutation,
  useGetEmailTemplateQuery,
  useUpdateEmailTemplateMutation,
  useDeleteEmailTemplateMutation,
  useGetNotificationTemplatesQuery,
  useCreateNotificationTemplateMutation,
  useGetNotificationTemplateQuery,
  useUpdateNotificationTemplateMutation,
  useDeleteNotificationTemplateMutation,
  useGetDocumentTemplatesQuery,
  useCreateDocumentTemplateMutation,
  useDeleteDocumentTemplateMutation,
} = injectedRtkApi
