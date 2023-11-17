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
export type PersonBase = {
  full_name: string
  email: string
  address: string
  phone_number: string
}
export type Person = PersonBase & {
  id: number
  url: string
  support_contact_preferences: {
    display: string
    value: string
    choices: string[][]
  }
}
export type Error = {
  detail?: string | object | (string | object | any)[]
  nonFieldErrors?: string[]
}
export type PersonCreate = PersonBase & {
  support_contact_preferences: string
}
export const {
  useGetPeopleQuery,
  useCreatePersonMutation,
  useSearchPeopleQuery,
  useGetPersonQuery,
  useUpdatePersonMutation,
  useDeletePersonMutation,
} = injectedRtkApi
