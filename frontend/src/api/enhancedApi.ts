import { generatedApi } from './api.generated'

const ENTITY_TYPES = ['CASE', 'EMAIL', 'TASK_COMMENT'] as const

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
    getTaskComments: {
      providesTags: [{ type: 'TASK_COMMENT' }],
    },
    createTaskComment: {
      invalidatesTags: [{ type: 'TASK_COMMENT' }],
    },
    getTaskAttachments: {
      providesTags: [{ type: 'TASK_ATTACHMENT' }],
    },
    createTaskAttachment: {
      invalidatesTags: [{ type: 'TASK_ATTACHMENT' }],
    },
    deleteTaskAttachment: {
      invalidatesTags: [{ type: 'TASK_ATTACHMENT' }],
    },
    updateTaskStatus: {
      invalidatesTags: [{ type: 'TASK_COMMENT' }],
    },
  },
})

export default enhancedApi
