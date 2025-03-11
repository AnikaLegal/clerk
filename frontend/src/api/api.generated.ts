import { baseApi as api } from "./baseApi";
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
        method: "PATCH",
        body: queryArg.issueUpdate,
      }),
    }),
    createCaseNote: build.mutation<
      CreateCaseNoteApiResponse,
      CreateCaseNoteApiArg
    >({
      query: (queryArg) => ({
        url: `/clerk/api/case/${queryArg.id}/note/`,
        method: "POST",
        body: queryArg.issueNoteCreate,
      }),
    }),
    getCaseDocuments: build.query<
      GetCaseDocumentsApiResponse,
      GetCaseDocumentsApiArg
    >({
      query: (queryArg) => ({ url: `/clerk/api/case/${queryArg.id}/docs/` }),
    }),
    getCaseServices: build.query<
      GetCaseServicesApiResponse,
      GetCaseServicesApiArg
    >({
      query: (queryArg) => ({
        url: `/clerk/api/case/${queryArg.id}/services/`,
        params: {
          category: queryArg.category,
          type: queryArg["type"],
        },
      }),
    }),
    createCaseService: build.mutation<
      CreateCaseServiceApiResponse,
      CreateCaseServiceApiArg
    >({
      query: (queryArg) => ({
        url: `/clerk/api/case/${queryArg.id}/services/`,
        method: "POST",
        body: queryArg.serviceCreate,
      }),
    }),
    getCaseService: build.query<
      GetCaseServiceApiResponse,
      GetCaseServiceApiArg
    >({
      query: (queryArg) => ({
        url: `/clerk/api/case/${queryArg.id}/services/${queryArg.serviceId}/`,
      }),
    }),
    updateCaseService: build.mutation<
      UpdateCaseServiceApiResponse,
      UpdateCaseServiceApiArg
    >({
      query: (queryArg) => ({
        url: `/clerk/api/case/${queryArg.id}/services/${queryArg.serviceId}/`,
        method: "PATCH",
        body: queryArg.serviceCreate,
      }),
    }),
    deleteCaseService: build.mutation<
      DeleteCaseServiceApiResponse,
      DeleteCaseServiceApiArg
    >({
      query: (queryArg) => ({
        url: `/clerk/api/case/${queryArg.id}/services/${queryArg.serviceId}/`,
        method: "DELETE",
      }),
    }),
    getEmailThreads: build.query<
      GetEmailThreadsApiResponse,
      GetEmailThreadsApiArg
    >({
      query: (queryArg) => ({
        url: `/clerk/api/email/${queryArg.id}/`,
        params: {
          slug: queryArg.slug,
        },
      }),
    }),
    createEmail: build.mutation<CreateEmailApiResponse, CreateEmailApiArg>({
      query: (queryArg) => ({
        url: `/clerk/api/email/${queryArg.id}/create/`,
        method: "POST",
        body: queryArg.emailCreate,
      }),
    }),
    getEmail: build.query<GetEmailApiResponse, GetEmailApiArg>({
      query: (queryArg) => ({
        url: `/clerk/api/email/${queryArg.id}/${queryArg.emailId}/`,
      }),
    }),
    updateEmail: build.mutation<UpdateEmailApiResponse, UpdateEmailApiArg>({
      query: (queryArg) => ({
        url: `/clerk/api/email/${queryArg.id}/${queryArg.emailId}/`,
        method: "PATCH",
        body: queryArg.emailCreate,
      }),
    }),
    deleteEmail: build.mutation<DeleteEmailApiResponse, DeleteEmailApiArg>({
      query: (queryArg) => ({
        url: `/clerk/api/email/${queryArg.id}/${queryArg.emailId}/`,
        method: "DELETE",
      }),
    }),
    createEmailAttachment: build.mutation<
      CreateEmailAttachmentApiResponse,
      CreateEmailAttachmentApiArg
    >({
      query: (queryArg) => ({
        url: `/clerk/api/email/${queryArg.id}/${queryArg.emailId}/attachment/`,
        method: "POST",
        body: queryArg.emailAttachmentCreate,
      }),
    }),
    deleteEmailAttachment: build.mutation<
      DeleteEmailAttachmentApiResponse,
      DeleteEmailAttachmentApiArg
    >({
      query: (queryArg) => ({
        url: `/clerk/api/email/${queryArg.id}/${queryArg.emailId}/attachment/${queryArg.attachmentId}/`,
        method: "DELETE",
      }),
    }),
    uploadEmailAttachmentToSharepoint: build.mutation<
      UploadEmailAttachmentToSharepointApiResponse,
      UploadEmailAttachmentToSharepointApiArg
    >({
      query: (queryArg) => ({
        url: `/clerk/api/email/${queryArg.id}/${queryArg.emailId}/attachment/${queryArg.attachmentId}/sharepoint/`,
        method: "POST",
      }),
    }),
    downloadEmailAttachmentFromSharepoint: build.mutation<
      DownloadEmailAttachmentFromSharepointApiResponse,
      DownloadEmailAttachmentFromSharepointApiArg
    >({
      query: (queryArg) => ({
        url: `/clerk/api/email/${queryArg.id}/${queryArg.emailId}/attachment/sharepoint/${queryArg.sharepointId}/`,
        method: "POST",
      }),
    }),
    getNotes: build.query<GetNotesApiResponse, GetNotesApiArg>({
      query: (queryArg) => ({
        url: `/clerk/api/note/`,
        params: {
          page: queryArg.page,
          issue: queryArg.issue,
          creator: queryArg.creator,
          note_type: queryArg.noteType,
          reviewee: queryArg.reviewee,
        },
      }),
    }),
    getPeople: build.query<GetPeopleApiResponse, GetPeopleApiArg>({
      query: () => ({ url: `/clerk/api/person/` }),
    }),
    createPerson: build.mutation<CreatePersonApiResponse, CreatePersonApiArg>({
      query: (queryArg) => ({
        url: `/clerk/api/person/`,
        method: "POST",
        body: queryArg.personCreate,
      }),
    }),
    searchPeople: build.query<SearchPeopleApiResponse, SearchPeopleApiArg>({
      query: (queryArg) => ({
        url: `/clerk/api/person/search/`,
        params: {
          query: queryArg.query,
        },
      }),
    }),
    getPerson: build.query<GetPersonApiResponse, GetPersonApiArg>({
      query: (queryArg) => ({ url: `/clerk/api/person/${queryArg.id}/` }),
    }),
    updatePerson: build.mutation<UpdatePersonApiResponse, UpdatePersonApiArg>({
      query: (queryArg) => ({
        url: `/clerk/api/person/${queryArg.id}/`,
        method: "PUT",
        body: queryArg.personCreate,
      }),
    }),
    deletePerson: build.mutation<DeletePersonApiResponse, DeletePersonApiArg>({
      query: (queryArg) => ({
        url: `/clerk/api/person/${queryArg.id}/`,
        method: "DELETE",
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
        method: "PATCH",
        body: queryArg.tenancyCreate,
      }),
    }),
    updateClient: build.mutation<UpdateClientApiResponse, UpdateClientApiArg>({
      query: (queryArg) => ({
        url: `/clerk/api/client/${queryArg.id}/`,
        method: "PATCH",
        body: queryArg.clientCreate,
      }),
    }),
    getUsers: build.query<GetUsersApiResponse, GetUsersApiArg>({
      query: (queryArg) => ({
        url: `/clerk/api/account/`,
        params: {
          name: queryArg.name,
          group: queryArg.group,
          is_active: queryArg.isActive,
          sort: queryArg.sort,
        },
      }),
    }),
    createUser: build.mutation<CreateUserApiResponse, CreateUserApiArg>({
      query: (queryArg) => ({
        url: `/clerk/api/account/`,
        method: "POST",
        body: queryArg.userCreate,
      }),
    }),
    getUser: build.query<GetUserApiResponse, GetUserApiArg>({
      query: (queryArg) => ({ url: `/clerk/api/account/${queryArg.id}/` }),
    }),
    updateUser: build.mutation<UpdateUserApiResponse, UpdateUserApiArg>({
      query: (queryArg) => ({
        url: `/clerk/api/account/${queryArg.id}/`,
        method: "PATCH",
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
        method: "POST",
      }),
    }),
    promoteUserAccountPermissions: build.mutation<
      PromoteUserAccountPermissionsApiResponse,
      PromoteUserAccountPermissionsApiArg
    >({
      query: (queryArg) => ({
        url: `/clerk/api/account/${queryArg.id}/perms-promote/`,
        method: "POST",
      }),
    }),
    demoteUserAccountPermissions: build.mutation<
      DemoteUserAccountPermissionsApiResponse,
      DemoteUserAccountPermissionsApiArg
    >({
      query: (queryArg) => ({
        url: `/clerk/api/account/${queryArg.id}/perms-demote/`,
        method: "POST",
      }),
    }),
    getEmailTemplates: build.query<
      GetEmailTemplatesApiResponse,
      GetEmailTemplatesApiArg
    >({
      query: (queryArg) => ({
        url: `/clerk/api/template-email/`,
        params: {
          name: queryArg.name,
          topic: queryArg.topic,
        },
      }),
    }),
    createEmailTemplate: build.mutation<
      CreateEmailTemplateApiResponse,
      CreateEmailTemplateApiArg
    >({
      query: (queryArg) => ({
        url: `/clerk/api/template-email/`,
        method: "POST",
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
        method: "PATCH",
        body: queryArg.emailTemplateCreate,
      }),
    }),
    deleteEmailTemplate: build.mutation<
      DeleteEmailTemplateApiResponse,
      DeleteEmailTemplateApiArg
    >({
      query: (queryArg) => ({
        url: `/clerk/api/template-email/${queryArg.id}/`,
        method: "DELETE",
      }),
    }),
    getNotificationTemplates: build.query<
      GetNotificationTemplatesApiResponse,
      GetNotificationTemplatesApiArg
    >({
      query: (queryArg) => ({
        url: `/clerk/api/template-notify/`,
        params: {
          name: queryArg.name,
          topic: queryArg.topic,
        },
      }),
    }),
    createNotificationTemplate: build.mutation<
      CreateNotificationTemplateApiResponse,
      CreateNotificationTemplateApiArg
    >({
      query: (queryArg) => ({
        url: `/clerk/api/template-notify/`,
        method: "POST",
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
        method: "PATCH",
        body: queryArg.notificationTemplateCreate,
      }),
    }),
    deleteNotificationTemplate: build.mutation<
      DeleteNotificationTemplateApiResponse,
      DeleteNotificationTemplateApiArg
    >({
      query: (queryArg) => ({
        url: `/clerk/api/template-notify/${queryArg.id}/`,
        method: "DELETE",
      }),
    }),
    getDocumentTemplates: build.query<
      GetDocumentTemplatesApiResponse,
      GetDocumentTemplatesApiArg
    >({
      query: (queryArg) => ({
        url: `/clerk/api/template-doc/`,
        params: {
          name: queryArg.name,
          topic: queryArg.topic,
        },
      }),
    }),
    createDocumentTemplate: build.mutation<
      CreateDocumentTemplateApiResponse,
      CreateDocumentTemplateApiArg
    >({
      query: (queryArg) => ({
        url: `/clerk/api/template-doc/`,
        method: "POST",
        body: queryArg.documentTemplateCreate,
      }),
    }),
    deleteDocumentTemplate: build.mutation<
      DeleteDocumentTemplateApiResponse,
      DeleteDocumentTemplateApiArg
    >({
      query: (queryArg) => ({
        url: `/clerk/api/template-doc/${queryArg.id}/`,
        method: "DELETE",
      }),
    }),
    getTasks: build.query<GetTasksApiResponse, GetTasksApiArg>({
      query: (queryArg) => ({
        url: `/clerk/api/task/`,
        params: {
          q: queryArg.q,
          type: queryArg["type"],
          name: queryArg.name,
          status: queryArg.status,
          is_open: queryArg.isOpen,
          is_suspended: queryArg.isSuspended,
          issue: queryArg.issue,
          assigned_to: queryArg.assignedTo,
          issue__topic: queryArg.issueTopic,
        },
      }),
    }),
    createTask: build.mutation<CreateTaskApiResponse, CreateTaskApiArg>({
      query: (queryArg) => ({
        url: `/clerk/api/task/`,
        method: "POST",
        body: queryArg.taskCreate,
      }),
    }),
    getTask: build.query<GetTaskApiResponse, GetTaskApiArg>({
      query: (queryArg) => ({ url: `/clerk/api/task/${queryArg.id}/` }),
    }),
    updateTask: build.mutation<UpdateTaskApiResponse, UpdateTaskApiArg>({
      query: (queryArg) => ({
        url: `/clerk/api/task/${queryArg.id}/`,
        method: "PATCH",
        body: queryArg.taskCreate,
      }),
    }),
    deleteTask: build.mutation<DeleteTaskApiResponse, DeleteTaskApiArg>({
      query: (queryArg) => ({
        url: `/clerk/api/task/${queryArg.id}/`,
        method: "DELETE",
      }),
    }),
    getTaskActivity: build.query<
      GetTaskActivityApiResponse,
      GetTaskActivityApiArg
    >({
      query: (queryArg) => ({
        url: `/clerk/api/task/${queryArg.id}/activity/`,
      }),
    }),
    createTaskComment: build.mutation<
      CreateTaskCommentApiResponse,
      CreateTaskCommentApiArg
    >({
      query: (queryArg) => ({
        url: `/clerk/api/task/${queryArg.id}/comments/`,
        method: "POST",
        body: queryArg.taskCommentCreate,
      }),
    }),
    getTaskAttachments: build.query<
      GetTaskAttachmentsApiResponse,
      GetTaskAttachmentsApiArg
    >({
      query: (queryArg) => ({
        url: `/clerk/api/task/${queryArg.id}/attachments/`,
      }),
    }),
    createTaskAttachment: build.mutation<
      CreateTaskAttachmentApiResponse,
      CreateTaskAttachmentApiArg
    >({
      query: (queryArg) => ({
        url: `/clerk/api/task/${queryArg.id}/attachments/`,
        method: "POST",
        body: queryArg.taskAttachmentCreate,
      }),
    }),
    deleteTaskAttachment: build.mutation<
      DeleteTaskAttachmentApiResponse,
      DeleteTaskAttachmentApiArg
    >({
      query: (queryArg) => ({
        url: `/clerk/api/task/${queryArg.id}/attachments/${queryArg.attachmentId}/`,
        method: "DELETE",
      }),
    }),
    updateTaskStatus: build.mutation<
      UpdateTaskStatusApiResponse,
      UpdateTaskStatusApiArg
    >({
      query: (queryArg) => ({
        url: `/clerk/api/task/${queryArg.id}/status_change/`,
        method: "PATCH",
        body: queryArg.taskStatusUpdate,
      }),
    }),
    createTaskRequest: build.mutation<
      CreateTaskRequestApiResponse,
      CreateTaskRequestApiArg
    >({
      query: (queryArg) => ({
        url: `/clerk/api/task/${queryArg.id}/request/create/`,
        method: "POST",
        body: queryArg.taskRequestCreate,
      }),
    }),
    updateTaskRequest: build.mutation<
      UpdateTaskRequestApiResponse,
      UpdateTaskRequestApiArg
    >({
      query: (queryArg) => ({
        url: `/clerk/api/task/${queryArg.id}/request/${queryArg.requestId}/`,
        method: "PATCH",
        body: queryArg.taskRequestUpdate,
      }),
    }),
    getTaskTriggers: build.query<
      GetTaskTriggersApiResponse,
      GetTaskTriggersApiArg
    >({
      query: () => ({ url: `/clerk/api/template-task/` }),
    }),
    createTaskTrigger: build.mutation<
      CreateTaskTriggerApiResponse,
      CreateTaskTriggerApiArg
    >({
      query: (queryArg) => ({
        url: `/clerk/api/template-task/`,
        method: "POST",
        body: queryArg.taskTriggerCreate,
      }),
    }),
    getTaskTrigger: build.query<
      GetTaskTriggerApiResponse,
      GetTaskTriggerApiArg
    >({
      query: (queryArg) => ({
        url: `/clerk/api/template-task/${queryArg.id}/`,
      }),
    }),
    updateTaskTrigger: build.mutation<
      UpdateTaskTriggerApiResponse,
      UpdateTaskTriggerApiArg
    >({
      query: (queryArg) => ({
        url: `/clerk/api/template-task/${queryArg.id}/`,
        method: "PATCH",
        body: queryArg.taskTriggerCreate,
      }),
    }),
    deleteTaskTrigger: build.mutation<
      DeleteTaskTriggerApiResponse,
      DeleteTaskTriggerApiArg
    >({
      query: (queryArg) => ({
        url: `/clerk/api/template-task/${queryArg.id}/`,
        method: "DELETE",
      }),
    }),
  }),
  overrideExisting: false,
});
export { injectedRtkApi as generatedApi };
export type GetCasesApiResponse = /** status 200 Successful response. */ {
  current: number;
  next: number | null;
  prev: number | null;
  page_count: number;
  item_count: number;
  results: Issue[];
};
export type GetCasesApiArg = {
  page?: number;
  search?: string;
  topic?: string;
  stage?: string;
  outcome?: string;
  isOpen?: string;
  paralegal?: string;
  lawyer?: string;
};
export type GetCaseApiResponse = /** status 200 Successful response. */ {
  issue: Issue;
  tenancy: Tenancy;
  notes: IssueNote[];
};
export type GetCaseApiArg = {
  /** Entity ID */
  id: string;
};
export type UpdateCaseApiResponse =
  /** status 200 Successful response. */ Issue;
export type UpdateCaseApiArg = {
  /** Entity ID */
  id: string;
  /** Successful response. */
  issueUpdate: IssueUpdate;
};
export type CreateCaseNoteApiResponse =
  /** status 201 Successful response. */ IssueNote;
export type CreateCaseNoteApiArg = {
  /** Entity ID */
  id: string;
  /** Successful response. */
  issueNoteCreate: IssueNoteCreate;
};
export type GetCaseDocumentsApiResponse =
  /** status 200 Successful response. */ {
    sharepoint_url: string;
    documents: SharepointDocument[];
  };
export type GetCaseDocumentsApiArg = {
  /** Entity ID */
  id: string;
};
export type GetCaseServicesApiResponse =
  /** status 200 Successful response. */ Service[];
export type GetCaseServicesApiArg = {
  /** Entity ID */
  id: string;
  category?: string;
  type?: string;
};
export type CreateCaseServiceApiResponse =
  /** status 201 Successful response. */ Service;
export type CreateCaseServiceApiArg = {
  /** Entity ID */
  id: string;
  /** Successful response. */
  serviceCreate: ServiceCreate;
};
export type GetCaseServiceApiResponse =
  /** status 200 Successful response. */ Service;
export type GetCaseServiceApiArg = {
  /** Case ID */
  id: string;
  /** Service ID */
  serviceId: number;
};
export type UpdateCaseServiceApiResponse =
  /** status 200 Successful response. */ Service;
export type UpdateCaseServiceApiArg = {
  /** Case ID */
  id: string;
  /** Service ID */
  serviceId: number;
  /** Successful response. */
  serviceCreate: ServiceCreate;
};
export type DeleteCaseServiceApiResponse = unknown;
export type DeleteCaseServiceApiArg = {
  /** Case ID */
  id: string;
  /** Service ID */
  serviceId: number;
};
export type GetEmailThreadsApiResponse =
  /** status 200 Successful response. */ EmailThread[];
export type GetEmailThreadsApiArg = {
  /** Case ID */
  id: string;
  slug?: string;
};
export type CreateEmailApiResponse =
  /** status 201 Successful response. */ Email;
export type CreateEmailApiArg = {
  /** Case ID */
  id: string;
  emailCreate: EmailCreate;
};
export type GetEmailApiResponse = /** status 200 Successful response. */ Email;
export type GetEmailApiArg = {
  /** Case ID */
  id: string;
  /** Email ID */
  emailId: number;
};
export type UpdateEmailApiResponse =
  /** status 200 Successful response. */ Email;
export type UpdateEmailApiArg = {
  /** Case ID */
  id: string;
  /** Email ID */
  emailId: number;
  /** Successful response. */
  emailCreate: EmailCreate;
};
export type DeleteEmailApiResponse = unknown;
export type DeleteEmailApiArg = {
  /** Case ID */
  id: string;
  /** Email ID */
  emailId: number;
};
export type CreateEmailAttachmentApiResponse =
  /** status 201 Successful response. */ EmailAttachment;
export type CreateEmailAttachmentApiArg = {
  /** Case ID */
  id: string;
  /** Email ID */
  emailId: number;
  emailAttachmentCreate: EmailAttachmentCreate;
};
export type DeleteEmailAttachmentApiResponse = unknown;
export type DeleteEmailAttachmentApiArg = {
  /** Case ID */
  id: string;
  /** Email ID */
  emailId: number;
  /** Email Attachment ID */
  attachmentId: number;
};
export type UploadEmailAttachmentToSharepointApiResponse = unknown;
export type UploadEmailAttachmentToSharepointApiArg = {
  /** Case ID */
  id: string;
  /** Email ID */
  emailId: number;
  /** Email Attachment ID */
  attachmentId: number;
};
export type DownloadEmailAttachmentFromSharepointApiResponse = unknown;
export type DownloadEmailAttachmentFromSharepointApiArg = {
  /** Case ID */
  id: string;
  /** Email ID */
  emailId: number;
  /** Sharepoint ID */
  sharepointId: string;
};
export type GetNotesApiResponse = /** status 200 Successful response. */ {
  current: number;
  next: number | null;
  prev: number | null;
  page_count: number;
  item_count: number;
  results: IssueNote[];
};
export type GetNotesApiArg = {
  page?: number;
  issue?: string;
  creator?: string;
  noteType?: string;
  reviewee?: string;
};
export type GetPeopleApiResponse =
  /** status 200 Successful response. */ Person[];
export type GetPeopleApiArg = void;
export type CreatePersonApiResponse =
  /** status 201 Successful response. */ Person;
export type CreatePersonApiArg = {
  personCreate: PersonCreate;
};
export type SearchPeopleApiResponse =
  /** status 200 Successful response. */ Person[];
export type SearchPeopleApiArg = {
  query: string;
};
export type GetPersonApiResponse =
  /** status 200 Successful response. */ Person;
export type GetPersonApiArg = {
  /** Entity ID */
  id: number;
};
export type UpdatePersonApiResponse =
  /** status 200 Successful response. */ Person;
export type UpdatePersonApiArg = {
  /** Entity ID */
  id: number;
  /** Successful response. */
  personCreate: PersonCreate;
};
export type DeletePersonApiResponse = unknown;
export type DeletePersonApiArg = {
  /** Entity ID */
  id: number;
};
export type GetTenancyApiResponse =
  /** status 200 Successful response. */ Tenancy;
export type GetTenancyApiArg = {
  /** Entity ID */
  id: number;
};
export type UpdateTenancyApiResponse =
  /** status 200 Successful response. */ Tenancy;
export type UpdateTenancyApiArg = {
  /** Entity ID */
  id: number;
  /** Successful response. */
  tenancyCreate: TenancyCreate;
};
export type UpdateClientApiResponse =
  /** status 200 Successful response. */ Client;
export type UpdateClientApiArg = {
  /** Entity ID */
  id: string;
  /** Successful response. */
  clientCreate: ClientCreate;
};
export type GetUsersApiResponse = /** status 200 Successful response. */ User[];
export type GetUsersApiArg = {
  name?: string;
  group?: string;
  isActive?: boolean;
  sort?:
    | "case_capacity"
    | "-case_capacity"
    | "date_joined"
    | "-date_joined"
    | "email"
    | "-email"
    | "first_name"
    | "-first_name"
    | "last_name"
    | "-last_name";
};
export type CreateUserApiResponse = /** status 201 Successful response. */ User;
export type CreateUserApiArg = {
  userCreate: UserCreate;
};
export type GetUserApiResponse = /** status 200 Successful response. */ User;
export type GetUserApiArg = {
  /** Entity ID */
  id: number;
};
export type UpdateUserApiResponse = /** status 200 Successful response. */ User;
export type UpdateUserApiArg = {
  /** Entity ID */
  id: number;
  /** Successful response. */
  userCreate: UserCreate;
};
export type GetUserAccountPermissionsApiResponse =
  /** status 200 Successful response. */ MicrosoftUserPermissions;
export type GetUserAccountPermissionsApiArg = {
  /** Entity ID */
  id: number;
};
export type ResyncUserAccountPermissionsApiResponse =
  /** status 201 Successful response. */ {
    account: User;
    permissions: MicrosoftUserPermissions;
  };
export type ResyncUserAccountPermissionsApiArg = {
  /** Entity ID */
  id: number;
};
export type PromoteUserAccountPermissionsApiResponse =
  /** status 201 Successful response. */ {
    account: User;
    permissions: MicrosoftUserPermissions;
  };
export type PromoteUserAccountPermissionsApiArg = {
  /** Entity ID */
  id: number;
};
export type DemoteUserAccountPermissionsApiResponse =
  /** status 201 Successful response. */ {
    account: User;
    permissions: MicrosoftUserPermissions;
  };
export type DemoteUserAccountPermissionsApiArg = {
  /** Entity ID */
  id: number;
};
export type GetEmailTemplatesApiResponse =
  /** status 200 Successful response. */ EmailTemplate[];
export type GetEmailTemplatesApiArg = {
  name?: string;
  topic?: string;
};
export type CreateEmailTemplateApiResponse =
  /** status 201 Successful response. */ EmailTemplate;
export type CreateEmailTemplateApiArg = {
  emailTemplateCreate: EmailTemplateCreate;
};
export type GetEmailTemplateApiResponse =
  /** status 200 Successful response. */ EmailTemplate;
export type GetEmailTemplateApiArg = {
  /** Entity ID */
  id: number;
};
export type UpdateEmailTemplateApiResponse =
  /** status 200 Successful response. */ EmailTemplate;
export type UpdateEmailTemplateApiArg = {
  /** Entity ID */
  id: number;
  /** Successful response. */
  emailTemplateCreate: EmailTemplateCreate;
};
export type DeleteEmailTemplateApiResponse = unknown;
export type DeleteEmailTemplateApiArg = {
  /** Entity ID */
  id: number;
};
export type GetNotificationTemplatesApiResponse =
  /** status 200 Successful response. */ NotificationTemplate[];
export type GetNotificationTemplatesApiArg = {
  name?: string;
  topic?: string;
};
export type CreateNotificationTemplateApiResponse =
  /** status 201 Successful response. */ NotificationTemplate;
export type CreateNotificationTemplateApiArg = {
  notificationTemplateCreate: NotificationTemplateCreate;
};
export type GetNotificationTemplateApiResponse =
  /** status 200 Successful response. */ NotificationTemplate;
export type GetNotificationTemplateApiArg = {
  /** Entity ID */
  id: number;
};
export type UpdateNotificationTemplateApiResponse =
  /** status 200 Successful response. */ NotificationTemplate;
export type UpdateNotificationTemplateApiArg = {
  /** Entity ID */
  id: number;
  /** Successful response. */
  notificationTemplateCreate: NotificationTemplateCreate;
};
export type DeleteNotificationTemplateApiResponse = unknown;
export type DeleteNotificationTemplateApiArg = {
  /** Entity ID */
  id: number;
};
export type GetDocumentTemplatesApiResponse =
  /** status 200 Successful response. */ DocumentTemplate[];
export type GetDocumentTemplatesApiArg = {
  name?: string;
  topic?: string;
};
export type CreateDocumentTemplateApiResponse = unknown;
export type CreateDocumentTemplateApiArg = {
  documentTemplateCreate: DocumentTemplateCreate;
};
export type DeleteDocumentTemplateApiResponse = unknown;
export type DeleteDocumentTemplateApiArg = {
  /** Entity ID */
  id: number;
};
export type GetTasksApiResponse =
  /** status 200 Successful response. */ TaskList[];
export type GetTasksApiArg = {
  q?: string;
  type?: string;
  name?: string;
  status?: string;
  isOpen?: string;
  isSuspended?: string;
  issue?: string;
  assignedTo?: number;
  issueTopic?: string;
};
export type CreateTaskApiResponse = /** status 201 Successful response. */ Task;
export type CreateTaskApiArg = {
  taskCreate: TaskCreate;
};
export type GetTaskApiResponse = /** status 200 Successful response. */ Task;
export type GetTaskApiArg = {
  /** Entity ID */
  id: number;
};
export type UpdateTaskApiResponse = /** status 200 Successful response. */ Task;
export type UpdateTaskApiArg = {
  /** Entity ID */
  id: number;
  /** Successful response. */
  taskCreate: TaskCreate;
};
export type DeleteTaskApiResponse = unknown;
export type DeleteTaskApiArg = {
  /** Entity ID */
  id: number;
};
export type GetTaskActivityApiResponse =
  /** status 200 Successful response. */ TaskActivity[];
export type GetTaskActivityApiArg = {
  /** Entity ID */
  id: number;
};
export type CreateTaskCommentApiResponse =
  /** status 201 Successful response. */ TaskComment;
export type CreateTaskCommentApiArg = {
  /** Entity ID */
  id: number;
  /** Successful response. */
  taskCommentCreate: TaskCommentCreate;
};
export type GetTaskAttachmentsApiResponse =
  /** status 200 Successful response. */ TaskAttachment[];
export type GetTaskAttachmentsApiArg = {
  /** Entity ID */
  id: number;
};
export type CreateTaskAttachmentApiResponse =
  /** status 201 Successful response. */ TaskAttachment;
export type CreateTaskAttachmentApiArg = {
  /** Entity ID */
  id: number;
  /** Successful response. */
  taskAttachmentCreate: TaskAttachmentCreate;
};
export type DeleteTaskAttachmentApiResponse = unknown;
export type DeleteTaskAttachmentApiArg = {
  /** Task ID */
  id: number;
  /** Attachment ID */
  attachmentId: number;
};
export type UpdateTaskStatusApiResponse =
  /** status 200 Successful response. */ Task;
export type UpdateTaskStatusApiArg = {
  /** Entity ID */
  id: number;
  taskStatusUpdate: TaskStatusUpdate;
};
export type CreateTaskRequestApiResponse =
  /** status 200 Successful response. */ TaskRequest;
export type CreateTaskRequestApiArg = {
  /** Entity ID */
  id: number;
  taskRequestCreate: TaskRequestCreate;
};
export type UpdateTaskRequestApiResponse =
  /** status 200 Successful response. */ Task;
export type UpdateTaskRequestApiArg = {
  /** Task ID */
  id: number;
  /** Request ID */
  requestId: number;
  taskRequestUpdate: TaskRequestUpdate;
};
export type GetTaskTriggersApiResponse =
  /** status 200 Successful response. */ TaskTrigger[];
export type GetTaskTriggersApiArg = void;
export type CreateTaskTriggerApiResponse =
  /** status 201 Successful response. */ TaskTrigger;
export type CreateTaskTriggerApiArg = {
  taskTriggerCreate: TaskTriggerCreate;
};
export type GetTaskTriggerApiResponse =
  /** status 200 Successful response. */ TaskTrigger;
export type GetTaskTriggerApiArg = {
  /** Entity ID */
  id: number;
};
export type UpdateTaskTriggerApiResponse =
  /** status 200 Successful response. */ TaskTrigger;
export type UpdateTaskTriggerApiArg = {
  /** Entity ID */
  id: number;
  /** Successful response. */
  taskTriggerCreate: TaskTriggerCreate;
};
export type DeleteTaskTriggerApiResponse = unknown;
export type DeleteTaskTriggerApiArg = {
  /** Entity ID */
  id: number;
};
export type IssueBase = {
  topic: string;
  stage: string;
  outcome: string | null;
  outcome_notes: string;
  provided_legal_services: boolean;
  is_open: boolean;
};
export type UserCreate = {
  first_name: string;
  last_name: string;
  email: string;
  username: string;
};
export type User = UserCreate & {
  id: number;
  case_capacity: number;
  is_intern: boolean;
  is_active: boolean;
  is_superuser: boolean;
  full_name: string;
  created_at: string;
  groups: string[];
  url: string;
  is_admin_or_better: boolean;
  is_lawyer_or_better: boolean;
  is_coordinator_or_better: boolean;
  is_paralegal_or_better: boolean;
  is_admin: boolean;
  is_lawyer: boolean;
  is_coordinator: boolean;
  is_paralegal: boolean;
  is_ms_account_set_up: boolean;
  ms_account_created_at: string | null;
  is_system_account: boolean;
};
export type TextChoiceField = {
  display: string;
  value: string;
  choices: string[][];
};
export type ClientBase = {
  first_name: string;
  last_name: string;
  preferred_name: string | null;
  email: string;
  phone_number: string;
  gender: string | null;
  pronouns: string | null;
  centrelink_support: boolean;
  eligibility_notes: string;
  requires_interpreter: TextChoiceField;
  primary_language_non_english: boolean;
  primary_language: string;
  is_aboriginal_or_torres_strait_islander: TextChoiceField;
  number_of_dependents: number | null;
  notes: string;
  date_of_birth: string | null;
};
export type TextChoiceListField = {
  display: string;
  value: string[];
  choices: string[][];
};
export type Client = ClientBase & {
  id: string;
  url: string;
  age: number;
  full_name: string;
  call_times: TextChoiceListField;
  eligibility_circumstances: TextChoiceListField;
};
export type TenancyBase = {
  address: string;
  suburb: string | null;
  postcode: string | null;
  started: string | null;
};
export type PersonBase = {
  full_name: string;
  email: string;
  address: string;
  phone_number: string;
};
export type Person = PersonBase & {
  id: number;
  url: string;
  support_contact_preferences: TextChoiceField;
};
export type Tenancy = TenancyBase & {
  id: number;
  url: string;
  is_on_lease: TextChoiceField;
  rental_circumstances: TextChoiceField;
  landlord: Person;
  agent: Person;
};
export type Issue = IssueBase & {
  id: string;
  topic_display: string;
  stage_display: string;
  outcome_display: string | null;
  fileref: string;
  is_sharepoint_set_up: boolean;
  paralegal: User | null;
  lawyer: User | null;
  client: Client;
  employment_status: TextChoiceListField;
  weekly_income: number | null;
  referrer: string;
  referrer_type: TextChoiceField;
  tenancy: Tenancy;
  weekly_rent: number | null;
  support_worker: Person | null;
  actionstep_id: number | null;
  created_at: string;
  url: string;
  answers: {
    [key: string]: string;
  };
  is_conflict_check: boolean | null;
  is_eligibility_check: boolean | null;
  next_review: string | null;
};
export type IssueNoteBase = {
  note_type: string;
  text: string;
  event: string | null;
  issue_id: string;
};
export type IssueNote = IssueNoteBase & {
  id: number;
  creator: User;
  text_display: string;
  created_at: string;
  reviewee: User | null;
};
export type Error = {
  detail?: string | object | (string | object | any)[];
  nonFieldErrors?: string[];
};
export type IssueUpdate = IssueBase & {
  paralegal_id: User;
  lawyer_id: User;
  support_worker_id: Person;
  weekly_rent: number | null;
  employment_status: TextChoiceListField;
  weekly_income: number | null;
  referrer: string;
  referrer_type: TextChoiceField;
};
export type IssueNoteCreate = IssueNoteBase & {
  creator_id: number;
};
export type SharepointDocument = {
  name: string;
  url: string;
  id: string;
  size: number;
  is_file: boolean;
};
export type ServiceBase = {
  issue_id: string;
  category: string;
  type: string;
  started_at: string;
  finished_at: string | null;
  count: number | null;
  notes: string | null;
};
export type Service = ServiceBase & {
  id: number;
};
export type ServiceCreate = ServiceBase & object;
export type EmailCreate = {
  issue: string;
  to_address: string;
  from_address: string;
  cc_addresses: string[];
  subject: string;
  text: string;
  html: string;
};
export type EmailAttachment = {
  id: number;
  url: string;
  name: string;
  sharepoint_state: string;
  content_type: string;
  email: number;
};
export type Email = EmailCreate & {
  id: number;
  created_at: string;
  processed_at: string | null;
  sender: User;
  state: string;
  reply_url: string;
  edit_url: string;
  attachments: EmailAttachment[];
};
export type EmailThread = {
  emails: Email[];
  subject: string;
  slug: string;
  most_recent: string;
  url: string;
};
export type EmailAttachmentCreate = {
  file: Blob;
};
export type PersonCreate = PersonBase & {
  support_contact_preferences: string;
};
export type TenancyCreate = TenancyBase & {
  is_on_lease: string;
  rental_circumstances: string;
  landlord_id?: number | null;
  agent_id?: number | null;
};
export type ClientCreate = ClientBase & {
  call_times: string[];
  employment_status: string[];
  eligibility_circumstances: string[];
};
export type MicrosoftUserPermissions = {
  has_coordinator_perms: boolean;
  paralegal_perm_issues: Issue[];
  paralegal_perm_missing_issues: Issue[];
};
export type EmailTemplateCreate = {
  name: string;
  topic: string;
  subject: string;
  text: string;
};
export type EmailTemplate = EmailTemplateCreate & {
  id: number;
  url: string;
  created_at: string;
};
export type NotificationTemplateBase = {
  name: string;
  topic: string;
  event_stage: string;
  raw_text: string;
  message_text: string;
};
export type NotificationTemplate = NotificationTemplateBase & {
  id: number;
  url: string;
  created_at: string;
  event: TextChoiceField;
  channel: TextChoiceField;
  target: TextChoiceField;
};
export type NotificationTemplateCreate = NotificationTemplateBase & {
  event: string;
  channel: string;
  target: string;
};
export type DocumentTemplate = {
  id: string;
  name: string;
  topic: string;
  url: string;
  created_at: string;
  modified_at: string;
};
export type DocumentTemplateCreate = {
  topic: string;
  files: Blob[];
};
export type TaskType =
  | "APPROVAL"
  | "CHECK"
  | "CONTACT"
  | "DRAFT"
  | "MANAGE"
  | "OTHER"
  | "REVIEW"
  | "SEND";
export type TaskStatus = "NOT_STARTED" | "IN_PROGRESS" | "DONE" | "NOT_DONE";
export type TaskListUser = {
  id: number;
  full_name: string;
  url: string;
};
export type TaskList = {
  id: number;
  type: TaskType;
  name: string;
  status: TaskStatus;
  is_open: boolean;
  is_suspended: boolean;
  due_at?: string | null;
  closed_at: string | null;
  is_urgent: boolean;
  is_approval_required: boolean;
  is_approval_pending: boolean;
  is_approved: boolean;
  days_open: number;
  url: string;
  issue: {
    id: string;
    topic: string;
    fileref: string;
    url: string;
  };
  assigned_to: TaskListUser;
  created_at: string;
  modified_at: string;
};
export type TaskBase = {
  name: string;
  description?: string;
  issue_id: string;
  assigned_to_id: number | null;
  due_at?: string | null;
  is_urgent?: boolean;
  is_approval_required?: boolean;
  is_approved?: boolean;
};
export type TaskRequest = {
  id: number;
  type: string;
  status: string;
  is_approved: boolean;
  from_task_id: number;
  from_user: TaskListUser;
  from_comment: string;
  to_task_id: number;
  to_user: TaskListUser;
  to_comment: string | null;
};
export type Task = TaskBase & {
  id: number;
  type: TaskType;
  status: TaskStatus;
  url: string;
  issue: Issue;
  assigned_to: User;
  is_open: boolean;
  is_suspended: boolean;
  is_approval_pending: boolean;
  closed_at: string | null;
  days_open: number;
  request: TaskRequest;
  created_at: string;
  modified_at: string;
};
export type TaskCreate = TaskBase & {
  type: TaskType;
  status?: TaskStatus;
};
export type TaskCommentBase = {
  text: string;
};
export type TaskComment = TaskCommentBase & {
  id: number;
  task_id: number;
  creator: {
    id: number;
    full_name: string;
    url: string;
  };
  created_at: string;
  modified_at: string;
};
export type TaskEvent = {
  id: number;
  type:
    | "APPROVAL_REQUEST"
    | "CANCELLED"
    | "REASSIGNED"
    | "REQUEST_ACCEPTED"
    | "REQUEST_DECLINED"
    | "RESUMED"
    | "STATUS_CHANGE"
    | "SUSPENDED";
  type_display: string;
  task_id: number;
  user?: TaskListUser;
  desc_html: string;
  note_html: string;
  created_at: string;
  modified_at: string;
};
export type TaskActivity = {
  id: number;
  task_id: number;
  type: "comment" | "event";
  data: TaskComment | TaskEvent;
  created_at: string;
  modified_at: string;
};
export type TaskCommentCreate = TaskCommentBase & {
  creator_id: number;
};
export type TaskAttachmentBase = {
  comment_id: number | null;
};
export type TaskAttachment = TaskAttachmentBase & {
  id: number;
  name: string;
  url: string;
  content_type: string;
};
export type TaskAttachmentCreate = TaskAttachmentBase & {
  file: Blob;
};
export type TaskStatusUpdate = {
  status: TaskStatus;
  comment?: string;
};
export type TaskRequestCreate = {
  type: "APPROVAL";
  to_user_id: number;
  name: string;
  comment: string;
};
export type TaskRequestUpdate = {
  status: "PENDING" | "DONE";
  is_approved?: boolean;
  to_comment?: string;
};
export type TaskTemplate = {
  id?: number;
  type: string;
  name: string;
  description?: string;
  due_in: number | null;
  is_urgent: boolean;
  is_approval_required: boolean;
};
export type TaskTriggerBase = {
  name: string;
  topic: string;
  event: string;
  tasks_assignment_role: string;
  event_stage?: string;
  templates: TaskTemplate[];
};
export type TaskTrigger = TaskTriggerBase & {
  id: number;
  url: string;
  created_at: string;
  modified_at: string;
};
export type TaskTriggerCreate = TaskTriggerBase & object;
export const {
  useGetCasesQuery,
  useGetCaseQuery,
  useUpdateCaseMutation,
  useCreateCaseNoteMutation,
  useGetCaseDocumentsQuery,
  useGetCaseServicesQuery,
  useCreateCaseServiceMutation,
  useGetCaseServiceQuery,
  useUpdateCaseServiceMutation,
  useDeleteCaseServiceMutation,
  useGetEmailThreadsQuery,
  useCreateEmailMutation,
  useGetEmailQuery,
  useUpdateEmailMutation,
  useDeleteEmailMutation,
  useCreateEmailAttachmentMutation,
  useDeleteEmailAttachmentMutation,
  useUploadEmailAttachmentToSharepointMutation,
  useDownloadEmailAttachmentFromSharepointMutation,
  useGetNotesQuery,
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
  useGetUserQuery,
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
  useGetTasksQuery,
  useCreateTaskMutation,
  useGetTaskQuery,
  useUpdateTaskMutation,
  useDeleteTaskMutation,
  useGetTaskActivityQuery,
  useCreateTaskCommentMutation,
  useGetTaskAttachmentsQuery,
  useCreateTaskAttachmentMutation,
  useDeleteTaskAttachmentMutation,
  useUpdateTaskStatusMutation,
  useCreateTaskRequestMutation,
  useUpdateTaskRequestMutation,
  useGetTaskTriggersQuery,
  useCreateTaskTriggerMutation,
  useGetTaskTriggerQuery,
  useUpdateTaskTriggerMutation,
  useDeleteTaskTriggerMutation,
} = injectedRtkApi;
