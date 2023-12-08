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
  /** status 201 Successful response. */ Person
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
  /** status 201 Successful response. */ Tenancy
export type UpdateTenancyApiArg = {
  /** Entity ID */
  id: number
  /** Successful response. */
  tenancyCreate: TenancyCreate
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
  employment_status: string[]
  rental_circumstances: string
  eligibility_circumstances: string[]
  referrer_type: string
  date_of_birth: string | null
}
export type Client = ClientBase & {
  id: string
  url: string
  age: number
  full_name: string
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
export const {
  useGetPeopleQuery,
  useCreatePersonMutation,
  useSearchPeopleQuery,
  useGetPersonQuery,
  useUpdatePersonMutation,
  useDeletePersonMutation,
  useGetTenancyQuery,
  useUpdateTenancyMutation,
} = injectedRtkApi
