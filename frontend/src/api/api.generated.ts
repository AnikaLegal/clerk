import { baseApi as api } from "./baseApi";
const injectedRtkApi = api.injectEndpoints({
  endpoints: (build) => ({
    getSubmission: build.query<GetSubmissionApiResponse, GetSubmissionApiArg>({
      query: (queryArg) => ({ url: `/clerk/api/submission/${queryArg.id}/` }),
    }),
    getCases: build.query<GetCasesApiResponse, GetCasesApiArg>({
      query: (queryArg) => ({
        url: `/clerk/api/case/`,
        params: {
          page: queryArg.page,
          page_size: queryArg.pageSize,
          search: queryArg.search,
          topic: queryArg.topic,
          stage: queryArg.stage,
          outcome: queryArg.outcome,
          is_open: queryArg.isOpen,
          paralegal: queryArg.paralegal,
          lawyer: queryArg.lawyer,
          client: queryArg.client,
        },
      }),
    }),
    createCase: build.mutation<CreateCaseApiResponse, CreateCaseApiArg>({
      query: (queryArg) => ({
        url: `/clerk/api/case/`,
        method: "POST",
        body: queryArg.issueCreate,
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
    getPeople: build.query<GetPeopleApiResponse, GetPeopleApiArg>({
      query: (queryArg) => ({
        url: `/clerk/api/person/`,
        params: {
          query: queryArg.query,
          page: queryArg.page,
        },
      }),
    }),
    createPerson: build.mutation<CreatePersonApiResponse, CreatePersonApiArg>({
      query: (queryArg) => ({
        url: `/clerk/api/person/`,
        method: "POST",
        body: queryArg.personCreate,
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
    getCaseDates: build.query<GetCaseDatesApiResponse, GetCaseDatesApiArg>({
      query: (queryArg) => ({
        url: `/clerk/api/date/`,
        params: {
          page: queryArg.page,
          page_size: queryArg.pageSize,
          q: queryArg.q,
          issue_id: queryArg.issueId,
          type: queryArg["type"],
          is_reviewed: queryArg.isReviewed,
        },
      }),
    }),
    createCaseDate: build.mutation<
      CreateCaseDateApiResponse,
      CreateCaseDateApiArg
    >({
      query: (queryArg) => ({
        url: `/clerk/api/date/`,
        method: "POST",
        body: queryArg.issueDateCreate,
      }),
    }),
    getCaseDate: build.query<GetCaseDateApiResponse, GetCaseDateApiArg>({
      query: (queryArg) => ({ url: `/clerk/api/date/${queryArg.id}/` }),
    }),
    updateCaseDate: build.mutation<
      UpdateCaseDateApiResponse,
      UpdateCaseDateApiArg
    >({
      query: (queryArg) => ({
        url: `/clerk/api/date/${queryArg.id}/`,
        method: "PATCH",
        body: queryArg.issueDateCreate,
      }),
    }),
    deleteCaseDate: build.mutation<
      DeleteCaseDateApiResponse,
      DeleteCaseDateApiArg
    >({
      query: (queryArg) => ({
        url: `/clerk/api/date/${queryArg.id}/`,
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
    getClients: build.query<GetClientsApiResponse, GetClientsApiArg>({
      query: (queryArg) => ({
        url: `/clerk/api/client/`,
        params: {
          page: queryArg.page,
          page_size: queryArg.pageSize,
          q: queryArg.q,
        },
      }),
    }),
    getClient: build.query<GetClientApiResponse, GetClientApiArg>({
      query: (queryArg) => ({ url: `/clerk/api/client/${queryArg.id}/` }),
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
    renameDocumentTemplate: build.mutation<
      RenameDocumentTemplateApiResponse,
      RenameDocumentTemplateApiArg
    >({
      query: (queryArg) => ({
        url: `/clerk/api/template-doc/${queryArg.id}/rename-file/`,
        method: "PATCH",
        body: queryArg.documentTemplateRename,
      }),
    }),
  }),
  overrideExisting: false,
});
export { injectedRtkApi as generatedApi };
export type GetSubmissionApiResponse =
  /** status 200 Successful response. */ Submission;
export type GetSubmissionApiArg = {
  /** Submission ID */
  id: string;
};
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
  pageSize?: number;
  search?: string;
  topic?: string;
  stage?: string;
  outcome?: string;
  isOpen?: string;
  paralegal?: string;
  lawyer?: string;
  client?: string;
};
export type CreateCaseApiResponse =
  /** status 201 Successful response. */ Issue;
export type CreateCaseApiArg = {
  issueCreate: IssueCreate;
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
  category?: ServiceCategory;
  type?: ServiceTypeDiscrete | ServiceTypeOngoing;
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
export type GetPeopleApiResponse = /** status 200 Successful response. */ {
  current: number;
  next: number | null;
  prev: number | null;
  page_count: number;
  item_count: number;
  results: Person[];
};
export type GetPeopleApiArg = {
  query?: string;
  /** Page number (pagination) */
  page?: number;
};
export type CreatePersonApiResponse =
  /** status 201 Successful response. */ Person;
export type CreatePersonApiArg = {
  personCreate: PersonCreate;
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
export type GetCaseDatesApiResponse = /** status 200 Successful response. */ {
  current: number;
  next: number | null;
  prev: number | null;
  page_count: number;
  item_count: number;
  results: IssueDate[];
};
export type GetCaseDatesApiArg = {
  page?: number;
  pageSize?: number;
  q?: string;
  /** Entity ID */
  issueId?: string;
  type?: IssueDateType;
  isReviewed?: boolean;
};
export type CreateCaseDateApiResponse =
  /** status 201 Successful response. */ IssueDate;
export type CreateCaseDateApiArg = {
  /** Successful response. */
  issueDateCreate: IssueDateCreate;
};
export type GetCaseDateApiResponse =
  /** status 200 Successful response. */ IssueDate;
export type GetCaseDateApiArg = {
  /** Date ID */
  id: number;
};
export type UpdateCaseDateApiResponse =
  /** status 200 Successful response. */ IssueDate;
export type UpdateCaseDateApiArg = {
  /** Date ID */
  id: number;
  /** Successful response. */
  issueDateCreate: IssueDateCreate;
};
export type DeleteCaseDateApiResponse = unknown;
export type DeleteCaseDateApiArg = {
  /** Date ID */
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
export type GetClientsApiResponse = /** status 200 Successful response. */ {
  current: number;
  next: number | null;
  prev: number | null;
  page_count: number;
  item_count: number;
  results: Client[];
};
export type GetClientsApiArg = {
  page?: number;
  pageSize?: number;
  q?: string;
};
export type GetClientApiResponse =
  /** status 200 Successful response. */ Client;
export type GetClientApiArg = {
  /** Entity ID */
  id: string;
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
export type RenameDocumentTemplateApiResponse = unknown;
export type RenameDocumentTemplateApiArg = {
  /** Entity ID */
  id: number;
  /** Successful response. */
  documentTemplateRename: DocumentTemplateRename;
};
export type BooleanYesNo = {
  label: "Yes" | "No";
  value: boolean;
};
export type ChoiceDisplay = {
  label: string;
  value: string;
};
export type SubmissionPerson = {
  name?: string | null;
  address?: string | null;
  email?: string | null;
  phone_number?: string | null;
  support_contact_preferences?: ChoiceDisplay | null;
};
export type SubmissionFiles = {
  url?: string;
  name?: string;
}[];
export type SubmissionAnswers = {
  client?: {
    first_name?: string | null;
    last_name?: string | null;
    preferred_name?: string | null;
    email?: string | null;
    date_of_birth?: string | null;
    phone_number?: string | null;
    gender?: string | null;
    centrelink_support?: BooleanYesNo | null;
    eligibility_notes?: string | null;
    requires_interpreter?: ChoiceDisplay | null;
    primary_language_non_english?: BooleanYesNo | null;
    primary_language?: string | null;
    is_aboriginal_or_torres_strait_islander?: ChoiceDisplay | null;
    number_of_dependents?: number | null;
    eligibility_circumstances?: ChoiceDisplay[] | null;
    call_times?: ChoiceDisplay[] | null;
    special_circumstances?: ChoiceDisplay[] | null;
  };
  tenancy?: {
    address?: string | null;
    suburb?: string | null;
    postcode?: string | null;
    is_on_lease?: ChoiceDisplay | null;
    rental_circumstances?: ChoiceDisplay | null;
    start_date?: string | null;
    landlord?: SubmissionPerson | null;
    agent?: SubmissionPerson | null;
  };
  issue?: {
    issues?: ChoiceDisplay[] | null;
    weekly_income?: number | null;
    employment_status?: ChoiceDisplay[] | null;
    referrer?: string | null;
    referrer_type?: ChoiceDisplay | null;
    weekly_rent?: number | null;
    support_worker?: SubmissionPerson | null;
  };
  topic_specific?: {
    REPAIRS?: {
      issue_start?: string | null;
      issue_photos?: SubmissionFiles | null;
      applied_vcat?: BooleanYesNo | null;
      vcat?: ChoiceDisplay[] | null;
      issue_description?: BooleanYesNo | null;
      required?: string[] | null;
    } | null;
    BONDS?: {
      claim_reasons?: string[] | null;
      cleaning_claim_amount?: number | null;
      cleaning_claim_description?: string | null;
      cleaning_documents?: SubmissionFiles | null;
      damage_caused_by_tenant?: BooleanYesNo | null;
      damage_claim_amount?: number | null;
      damage_claim_description?: string | null;
      damage_quote?: SubmissionFiles | null;
      has_landlord_made_rtba_application?: BooleanYesNo | null;
      landlord_intents_to_make_claim?: BooleanYesNo | null;
      locks_changed_by_tenant?: BooleanYesNo | null;
      locks_claim_amount?: number | null;
      locks_change_quote?: SubmissionFiles | null;
      money_is_owed_by_tenant?: BooleanYesNo | null;
      money_owed_claim_amount?: number | null;
      money_owed_claim_description?: string | null;
      move_out_date?: string | null;
      other_reasons_amount?: number | null;
      other_reasons_description?: string | null;
      tenant_has_rtba_application_copy?: BooleanYesNo | null;
      rtba_application?: SubmissionFiles | null;
    } | null;
    EVICTION_ARREARS?: {
      doc_delivery_time_notice_to_vacate?: string | null;
      has_notice?: BooleanYesNo | null;
      is_already_removed?: BooleanYesNo | null;
      is_unpaid_rent?: BooleanYesNo | null;
      is_vcat_date?: BooleanYesNo | null;
      notice_send_date?: string | null;
      notice_vacate_date?: string | null;
      payment_fail_description?: string | null;
      payment_fail_reason?: string[] | null;
      vcat_date?: string | null;
      documents?: SubmissionFiles | null;
      can_afford_payment_plan?: ChoiceDisplay | null;
      documents_provided?: string[] | null;
      delivery_method_notice_to_vacate?: string | null;
      delivery_method_other_docs?: string | null;
      delivery_method_possession_order?: string | null;
      doc_delivery_time_other_docs?: string | null;
      doc_delivery_time_possession_order?: string | null;
      is_on_payment_plan?: BooleanYesNo | null;
      miscellaneous?: string | null;
      payment_amount?: number | null;
      payment_fail_change?: string | null;
      rent_cycle?: string | null;
      rent_unpaid?: number | null;
    } | null;
    EVICTION_RETALIATORY?: {
      date_received_ntv?: string | null;
      has_notice?: BooleanYesNo | null;
      is_already_removed?: BooleanYesNo | null;
      ntv_type?: string | null;
      retaliatory_reason?: string[] | null;
      retaliatory_reason_other?: string | null;
      termination_date?: string | null;
      vcat_hearing?: BooleanYesNo | null;
      vcat_hearing_date?: string | null;
      documents?: SubmissionFiles | null;
    } | null;
    RENT_REDUCTION?: {
      issues?: string[] | null;
      issue_description?: string | null;
      issue_photos?: SubmissionFiles | null;
      issue_start?: string | null;
      is_notice_to_vacate?: BooleanYesNo | null;
      notice_to_vacate?: SubmissionFiles | null;
    } | null;
    HEALTH_CHECK?: {
      support_worker_authority?: SubmissionFiles | null;
      tenancy_documents?: SubmissionFiles | null;
    } | null;
    OTHER?: {
      issue_description?: string | null;
    } | null;
  } | null;
};
export type Submission = {
  id: string;
  answers_raw: {
    [key: string]: any;
  };
  answers: SubmissionAnswers | null;
  created_at: string;
};
export type IssueBase = {
  topic: string;
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
  is_coordinator_or_better: boolean;
  is_paralegal_or_better: boolean;
  is_admin: boolean;
  is_coordinator: boolean;
  is_paralegal: boolean;
  is_ms_account_set_up: boolean;
  ms_account_created_at: string | null;
};
export type ClientBase = {
  first_name: string;
  last_name: string;
  email: string;
};
export type TextChoiceField = {
  display: string;
  value: string;
  choices: string[][];
};
export type TextChoiceListField = {
  display: string;
  value: string[];
  choices: string[][];
};
export type Client = ClientBase & {
  id: string;
  date_of_birth: string | null;
  preferred_name: string | null;
  phone_number: string;
  gender: string | null;
  pronouns: string | null;
  centrelink_support: boolean;
  eligibility_notes: string;
  primary_language_non_english: boolean;
  primary_language: string;
  number_of_dependents: number | null;
  notes: string;
  url: string;
  age: number | null;
  full_name: string;
  contact_notes?: string;
  contact_restriction: TextChoiceField;
  requires_interpreter: TextChoiceField;
  is_aboriginal_or_torres_strait_islander: TextChoiceField;
  call_times: TextChoiceListField;
  eligibility_circumstances: TextChoiceListField;
};
export type TenancyBase = {
  address: string;
  suburb: string | null;
  postcode: string | null;
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
  started: string | null;
  url: string;
  is_on_lease: TextChoiceField;
  rental_circumstances: TextChoiceField;
  landlord: Person | null;
  agent: Person | null;
};
export type Issue = IssueBase & {
  id: string;
  topic_display: string;
  stage: string;
  stage_display: string;
  outcome: string | null;
  outcome_display: string | null;
  outcome_notes: string;
  fileref: string;
  provided_legal_services: boolean;
  is_open: boolean;
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
  } | null;
  is_conflict_check: boolean | null;
  is_eligibility_check: boolean | null;
  next_review: string | null;
  submission_id: string | null;
};
export type Error = {
  detail?: string | object | (string | object | any)[];
  non_field_errors?: string[];
};
export type ClientCreate = ClientBase & {
  date_of_birth?: string | null;
  preferred_name?: string | null;
  phone_number?: string;
  gender?: string | null;
  pronouns?: string | null;
  centrelink_support?: boolean;
  eligibility_notes?: string;
  primary_language_non_english?: boolean;
  primary_language?: string;
  number_of_dependents?: number | null;
  notes?: string;
  url?: string;
  age?: number | null;
  full_name?: string;
  contact_notes?: string;
  contact_restriction?: string;
  requires_interpreter?: string;
  is_aboriginal_or_torres_strait_islander?: string;
  call_times?: string[];
  eligibility_circumstances?: string[];
};
export type TenancyCreate = TenancyBase & {
  started?: string | null;
  is_on_lease?: string;
  rental_circumstances?: string;
  landlord_id?: number | null;
  agent_id?: number | null;
};
export type IssueCreate = IssueBase & {
  /** One of client_id or client is required. */
  client_id?: string;
  client?: ClientCreate;
  /** One of tenancy_id or tenancy is required. */
  tenancy_id?: number;
  tenancy?: TenancyCreate;
  stage?: string;
  outcome?: string | null;
  outcome_notes?: string;
  provided_legal_services?: boolean;
  paralegal_id?: number | null;
  lawyer_id?: number | null;
  support_worker_id?: number | null;
  employment_status?: string;
  weekly_income?: number | null;
  referrer?: string;
  referrer_type?: string;
  weekly_rent?: number | null;
};
export type IssueNoteBase = {
  note_type: string;
  text: string;
  event: string | null;
};
export type IssueNote = IssueNoteBase & {
  id: number;
  creator: User;
  text_display: string;
  created_at: string;
  reviewee: User | null;
};
export type IssueUpdate = {
  topic?: string;
  stage?: string;
  outcome?: string | null;
  outcome_notes?: string;
  provided_legal_services?: boolean;
  paralegal_id?: number | null;
  lawyer_id?: number | null;
  support_worker_id?: number | null;
  weekly_rent?: number | null;
  employment_status?: string;
  weekly_income?: number | null;
  referrer?: string;
  referrer_type?: string;
};
export type IssueNoteCreate = IssueNoteBase & {
  creator_id: number;
  issue_id: string;
};
export type SharepointDocument = {
  name: string;
  url: string;
  id: string;
  size: number;
  is_file: boolean;
};
export type ServiceCategory = "DISCRETE" | "ONGOING";
export type ServiceTypeDiscrete =
  | "LEGAL_ADVICE"
  | "LEGAL_TASK"
  | "GENERAL_INFORMATION"
  | "GENERAL_REFERRAL_SIMPLE"
  | "GENERAL_REFERRAL_FACILITATED";
export type ServiceTypeOngoing =
  | "LEGAL_SUPPORT"
  | "REPRESENTATION_COURT_TRIBUNAL"
  | "REPRESENTATION_OTHER";
export type ServiceBase = {
  category: ServiceCategory;
  type: ServiceTypeDiscrete | ServiceTypeOngoing;
  started_at: string;
  finished_at: string | null;
  count: number | null;
  notes: string | null;
};
export type Service = ServiceBase & {
  id: number;
  issue_id: string;
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
export type IssueDateType =
  | "FILING_DEADLINE"
  | "HEARING_LISTED"
  | "LIMITATION"
  | "NTV_TERMINATION"
  | "OTHER";
export type IssueDateHearingType = "IN_PERSON" | "VIRTUAL";
export type IssueDateBase = {
  type: IssueDateType;
  date: string;
  hearing_type?: IssueDateHearingType;
  hearing_location?: string;
};
export type IssueDate = IssueDateBase & {
  id: number;
  issue: Issue;
  notes: string;
  is_reviewed: boolean;
};
export type IssueDateCreate = IssueDateBase & {
  issue_id: string;
  notes?: string;
  is_reviewed?: boolean;
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
  id: number;
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
export type DocumentTemplateRename = {
  name: string;
};
export const {
  useGetSubmissionQuery,
  useGetCasesQuery,
  useCreateCaseMutation,
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
  useGetPeopleQuery,
  useCreatePersonMutation,
  useGetPersonQuery,
  useUpdatePersonMutation,
  useDeletePersonMutation,
  useGetCaseDatesQuery,
  useCreateCaseDateMutation,
  useGetCaseDateQuery,
  useUpdateCaseDateMutation,
  useDeleteCaseDateMutation,
  useGetTenancyQuery,
  useUpdateTenancyMutation,
  useGetClientsQuery,
  useGetClientQuery,
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
  useRenameDocumentTemplateMutation,
} = injectedRtkApi;
