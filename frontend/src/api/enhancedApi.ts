import { generatedApi } from './api.generated'

const ENTITY_TYPES = [
  'CASE',
  'EMAIL',
  'SERVICE',
  'TASKS',
  'TASK_ATTACHMENT',
  'TASK_ACTIVITY',
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
    getTask: {
      providesTags: [{ type: 'TASKS' }],
    },
    getTasks: {
      providesTags: [{ type: 'TASKS' }],
    },
    createTask: {
      invalidatesTags: [{ type: 'TASKS' }],
    },
    updateTask: {
      invalidatesTags: [{ type: 'TASK_ACTIVITY' }],
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
    getTaskActivity: {
      providesTags: [{ type: 'TASK_ACTIVITY' }],
    },
    updateTaskStatus: {
      invalidatesTags: [{ type: 'TASKS' }, { type: 'TASK_ACTIVITY' }],
    },
    createTaskRequest: {
      invalidatesTags: [{ type: 'TASKS' }, { type: 'TASK_ACTIVITY' }],
    },
    updateTaskRequest: {
      invalidatesTags: [{ type: 'TASKS' }, { type: 'TASK_ACTIVITY' }],
    },
    createTaskComment: {
      invalidatesTags: [{ type: 'TASK_ACTIVITY' }],
    },
  },
})

export default enhancedApi
