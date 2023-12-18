import { FetchArgs } from '@reduxjs/toolkit/query'
import { generatedApi } from './api.generated'

const ENTITY_TYPES = ['Thing'] as const

type AnyEntity = (typeof ENTITY_TYPES)[number]

export const listTagFor = <E extends AnyEntity>(type: E) => ({
  type,
  id: 'LIST' as const,
})

const enhancedApi = generatedApi.enhanceEndpoints({
  addTagTypes: ENTITY_TYPES,
  endpoints: {
    // Cache invalidation example.
    // getThings: {
    //   providesTags: [listTagFor("Thing")],
    // },
    // createThing: {
    //   invalidatesTags: [listTagFor("Thing")],
    // },
  },
})

export default enhancedApi
