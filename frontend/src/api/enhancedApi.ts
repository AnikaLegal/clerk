import { generatedApi } from './api.generated'

const ENTITY_TYPES = [
  'CASE',
  'EMAIL',
  'SERVICE',
  'DOCUMENT_TEMPLATE',
  'CLIENT',
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
    createClient: {
      invalidatesTags: [{ type: 'CLIENT' }],
    },
  },
})

export default enhancedApi
