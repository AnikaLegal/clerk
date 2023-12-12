import { baseApi as api } from './baseApi'
const injectedRtkApi = api.injectEndpoints({
  endpoints: (build) => ({
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
        method: 'PUT',
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
  }),
  overrideExisting: false,
})
export { injectedRtkApi as generatedApi }
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
export type PersonBase = {
  full_name: string
  email: string
  address: string
  phone_number: string
}
export type TextChoiceField = {
  display: string
  value: string
  choices: string[][]
}
export type Person = PersonBase & {
  id: number
  url: string
  support_contact_preferences: TextChoiceField
}
export type Error = {
  detail?: string | object | (string | object | any)[]
  nonFieldErrors?: string[]
}
export type PersonCreate = PersonBase & {
  support_contact_preferences: string
}
export type TenancyBase = {
  address: string
  suburb: string | null
  postcode: string | null
  started: string | null
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
export type Tenancy = TenancyBase & {
  id: number
  url: string
  is_on_lease: TextChoiceField
  landlord: Person
  agent: Person
  client: Client
}
export type TenancyCreate = TenancyBase & {
  is_on_lease: string
}
export type ClientCreate = ClientBase & {
  referrer_type: string
  call_times: string[]
  employment_status: string[]
  eligibility_circumstances: string[]
  rental_circumstances: string
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
export type Issue = {
  id: string
  topic: string
  topic_display: string
  stage_display: string
  stage: string
  outcome: string | null
  outcome_display: string | null
  outcome_notes: string
  provided_legal_services: boolean
  fileref: string
  paralegal: User
  lawyer: User
  client: Client
  support_worker: Person
  is_open: boolean
  is_sharepoint_set_up: boolean
  actionstep_id: number | null
  created_at: string
  url: string
}
export type MicrosoftUserPermissions = {
  has_coordinator_perms: boolean
  paralegal_perm_issues: Issue[]
  paralegal_perm_missing_issues: Issue[]
}
export const {
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
} = injectedRtkApi
