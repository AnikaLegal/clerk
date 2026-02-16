import { generatedApi } from './api.generated'

const ENTITY_TYPES = [
  'CASE',
  'CASE_DATE',
  'CLIENT',
  'DOCUMENT_TEMPLATE',
  'EMAIL',
  'SERVICE',
  'POTENTIAL_USER',
  'USER',
  'USER_PERMISSIONS',
] as const

const enhancedApi = generatedApi.enhanceEndpoints({
  addTagTypes: ENTITY_TYPES,
  endpoints: {
    // Cache invalidation settings.
    getCase: {
      providesTags: [{ type: 'CASE' }],
    },
    createCaseNote: {
      invalidatesTags: [{ type: 'CASE' }],
    },
    updateCase: {
      invalidatesTags: [{ type: 'CASE' }],
    },
    updateTenancy: {
      invalidatesTags: [{ type: 'CASE' }],
    },
    getEmailThreads: {
      providesTags: [{ type: 'EMAIL' }],
    },
    getEmail: {
      providesTags: [{ type: 'EMAIL' }],
    },
    uploadEmailAttachmentToSharepoint: {
      invalidatesTags: [{ type: 'EMAIL' }],
    },
    updateEmail: {
      invalidatesTags: [{ type: 'EMAIL' }],
    },
    deleteEmail: {
      invalidatesTags: [{ type: 'EMAIL' }],
    },
    createEmailAttachment: {
      invalidatesTags: [{ type: 'EMAIL' }],
    },
    downloadEmailAttachmentFromSharepoint: {
      invalidatesTags: [{ type: 'EMAIL' }],
    },
    deleteEmailAttachment: {
      invalidatesTags: [{ type: 'EMAIL' }],
    },
    getCaseServices: {
      providesTags: [{ type: 'SERVICE' }],
    },
    getCaseService: {
      providesTags: [{ type: 'SERVICE' }],
    },
    createCaseService: {
      invalidatesTags: [{ type: 'SERVICE' }],
    },
    updateCaseService: {
      invalidatesTags: [{ type: 'SERVICE' }],
    },
    deleteCaseService: {
      invalidatesTags: [{ type: 'SERVICE' }],
    },
    getDocumentTemplates: {
      providesTags: [{ type: 'DOCUMENT_TEMPLATE' }],
    },
    deleteDocumentTemplate: {
      invalidatesTags: [{ type: 'DOCUMENT_TEMPLATE' }],
    },
    renameDocumentTemplate: {
      invalidatesTags: [{ type: 'DOCUMENT_TEMPLATE' }],
    },
    getClients: {
      providesTags: [{ type: 'CLIENT' }],
    },
    getCaseDates: {
      providesTags: [{ type: 'CASE_DATE' }],
    },
    getCaseDate: {
      providesTags: [{ type: 'CASE_DATE' }],
    },
    createCaseDate: {
      invalidatesTags: [{ type: 'CASE_DATE' }],
    },
    updateCaseDate: {
      invalidatesTags: [{ type: 'CASE_DATE' }],
    },
    deleteCaseDate: {
      invalidatesTags: [{ type: 'CASE_DATE' }],
    },
    getUser: {
      providesTags: [{ type: 'USER' }],
    },
    getPotentialUsers: {
      providesTags: [{ type: 'POTENTIAL_USER' }],
    },
    createUser: {
      invalidatesTags: [{ type: 'USER' }, { type: 'POTENTIAL_USER' }],
    },
    updateUser: {
      invalidatesTags: [{ type: 'USER' }],
    },
    getUserAccountPermissions: {
      providesTags: [{ type: 'USER_PERMISSIONS' }],
    },
    resyncUserAccountPermissions: {
      invalidatesTags: [{ type: 'USER' }, { type: 'USER_PERMISSIONS' }],
    },
  },
})

export default enhancedApi
