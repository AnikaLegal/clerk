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
        body: queryArg.serviceUpdate,
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
        body: queryArg.emailUpdate,
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
          page_size: queryArg.pageSize,
          issue: queryArg.issue,
          creator: queryArg.creator,
          note_type: queryArg.noteType,
          reviewee: queryArg.reviewee,
        },
      }),
    }),
    getPeople: build.query<GetPeopleApiResponse, GetPeopleApiArg>({
      query: (queryArg) => ({
        url: `/clerk/api/person/`,
        params: {
          query: queryArg.query,
          page: queryArg.page,
          page_size: queryArg.pageSize,
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
        method: "PATCH",
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
        body: queryArg.issueDateUpdate,
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
        body: queryArg.tenancyUpdate,
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
        body: queryArg.clientUpdate,
      }),
    }),
    getUsers: build.query<GetUsersApiResponse, GetUsersApiArg>({
      query: (queryArg) => ({
        url: `/clerk/api/account/`,
        params: {
          page: queryArg.page,
          page_size: queryArg.pageSize,
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
        body: queryArg.userUpdate,
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
    getPotentialUsers: build.query<
      GetPotentialUsersApiResponse,
      GetPotentialUsersApiArg
    >({
      query: () => ({ url: `/clerk/api/account/potential/` }),
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
  results: IssueRead[];
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
  /** status 201 Successful response. */ IssueRead;
export type CreateCaseApiArg = {
  issueCreate: IssueCreate;
};
export type GetCaseApiResponse = /** status 200 Successful response. */ {
  issue: IssueRead;
  tenancy: Tenancy;
  notes: IssueNoteRead[];
};
export type GetCaseApiArg = {
  /** Entity ID */
  id: string;
};
export type UpdateCaseApiResponse =
  /** status 200 Successful response. */ IssueRead;
export type UpdateCaseApiArg = {
  /** Entity ID */
  id: string;
  /** Successful response. */
  issueUpdate: IssueUpdate;
};
export type CreateCaseNoteApiResponse =
  /** status 201 Successful response. */ IssueNoteRead;
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
  /** Request body for updating a case service. */
  serviceUpdate: ServiceUpdate;
};
export type DeleteCaseServiceApiResponse = unknown;
export type DeleteCaseServiceApiArg = {
  /** Case ID */
  id: string;
  /** Service ID */
  serviceId: number;
};
export type GetEmailThreadsApiResponse =
  /** status 200 Successful response. */ EmailThreadRead[];
export type GetEmailThreadsApiArg = {
  /** Case ID */
  id: string;
  slug?: string;
};
export type CreateEmailApiResponse =
  /** status 201 Successful response. */ EmailRead;
export type CreateEmailApiArg = {
  /** Case ID */
  id: string;
  emailCreate: EmailCreate;
};
export type GetEmailApiResponse =
  /** status 200 Successful response. */ EmailRead;
export type GetEmailApiArg = {
  /** Case ID */
  id: string;
  /** Email ID */
  emailId: number;
};
export type UpdateEmailApiResponse =
  /** status 200 Successful response. */ EmailRead;
export type UpdateEmailApiArg = {
  /** Case ID */
  id: string;
  /** Email ID */
  emailId: number;
  /** Successful response. */
  emailUpdate: EmailUpdate;
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
  results: IssueNoteRead[];
};
export type GetNotesApiArg = {
  page?: number;
  pageSize?: number;
  /** Entity ID */
  issue?: string;
  /** Creator account ID */
  creator?: number;
  noteType?: IssueNoteType;
  /** Reviewee account ID */
  reviewee?: number;
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
  /** Number of items per page (pagination) */
  pageSize?: number;
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
  results: IssueDateRead[];
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
  /** status 201 Successful response. */ IssueDateRead;
export type CreateCaseDateApiArg = {
  /** Successful response. */
  issueDateCreate: IssueDateCreate;
};
export type GetCaseDateApiResponse =
  /** status 200 Successful response. */ IssueDateRead;
export type GetCaseDateApiArg = {
  /** Date ID */
  id: number;
};
export type UpdateCaseDateApiResponse =
  /** status 200 Successful response. */ IssueDateRead;
export type UpdateCaseDateApiArg = {
  /** Date ID */
  id: number;
  /** Request body for updating a case date. */
  issueDateUpdate: IssueDateUpdate;
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
  /** Request body for updating a tenancy. */
  tenancyUpdate: TenancyUpdate;
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
  clientUpdate: ClientUpdate;
};
export type GetUsersApiResponse = /** status 200 Successful response. */ {
  current: number;
  next: number | null;
  prev: number | null;
  page_count: number;
  item_count: number;
  results: UserRead[];
};
export type GetUsersApiArg = {
  page?: number;
  pageSize?: number;
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
export type CreateUserApiResponse =
  /** status 201 Successful response. */ UserCreateRead;
export type CreateUserApiArg = {
  userCreate: UserCreate;
};
export type GetUserApiResponse =
  /** status 200 Successful response. */ UserRead;
export type GetUserApiArg = {
  /** Entity ID */
  id: number;
};
export type UpdateUserApiResponse =
  /** status 200 Successful response. */ UserRead;
export type UpdateUserApiArg = {
  /** Entity ID */
  id: number;
  /** Successful response. */
  userUpdate: UserUpdate;
};
export type GetUserAccountPermissionsApiResponse =
  /** status 200 Successful response. */ MicrosoftUserPermissionsRead;
export type GetUserAccountPermissionsApiArg = {
  /** Entity ID */
  id: number;
};
export type ResyncUserAccountPermissionsApiResponse =
  /** status 200 Successful response. */ {
    account: UserRead;
    permissions: MicrosoftUserPermissionsRead;
  };
export type ResyncUserAccountPermissionsApiArg = {
  /** Entity ID */
  id: number;
};
export type GetPotentialUsersApiResponse =
  /** status 200 Successful response. */ {
    email: string;
    first_name: string;
    last_name: string;
  }[];
export type GetPotentialUsersApiArg = void;
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
    annual_income_range?: ChoiceDisplay | null;
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
export type Error = {
  /** The category of error that occurred. */
  type: "validation_error" | "client_error" | "server_error";
  /** The individual errors that make up this response. */
  errors: {
    /** A machine-readable code identifying the error. */
    code: string;
    /** A human-readable description of the error. */
    detail: string;
    /** The name of the field that raised the error, or null for errors not tied to a specific field. Non-field validation errors use "non_field_errors".
     */
    attr: string | null;
  }[];
};
export type IssueBase = {
  topic: string;
};
export type TextChoiceListField = {
  display: string;
  value: string[];
  choices: string[][];
};
export type User = {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  case_capacity: number;
  is_intern: boolean;
  is_active: boolean;
  groups: TextChoiceListField;
  is_superuser: boolean;
  full_name: string;
  created_at: string;
  is_admin_or_better: boolean;
  is_coordinator_or_better: boolean;
  is_lawyer_or_better: boolean;
  is_paralegal_or_better: boolean;
  is_admin: boolean;
  is_coordinator: boolean;
  is_lawyer: boolean;
  is_paralegal: boolean;
  is_ms_account_set_up: boolean;
  ms_account_created_at: string | null;
};
export type UserRead = {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  url: string;
  case_capacity: number;
  is_intern: boolean;
  is_active: boolean;
  groups: TextChoiceListField;
  is_superuser: boolean;
  full_name: string;
  created_at: string;
  is_admin_or_better: boolean;
  is_coordinator_or_better: boolean;
  is_lawyer_or_better: boolean;
  is_paralegal_or_better: boolean;
  is_admin: boolean;
  is_coordinator: boolean;
  is_lawyer: boolean;
  is_paralegal: boolean;
  is_ms_account_set_up: boolean;
  ms_account_created_at: string | null;
};
export type TextChoiceField = {
  display: string;
  value: string;
  choices: string[][];
};
export type Client = {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
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
export type PersonBase = {
  full_name: string;
};
export type Person = PersonBase & {
  id: number;
  email: string;
  address: string;
  phone_number: string;
  url: string;
  support_contact_preferences: TextChoiceField;
};
export type Tenancy = {
  id: number;
  address: string;
  suburb: string | null;
  postcode: string | null;
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
  referrer: string;
  referrer_type: TextChoiceField;
  tenancy: Tenancy;
  weekly_rent: number | null;
  annual_income_range?: TextChoiceField;
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
export type IssueRead = IssueBase & {
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
  paralegal: UserRead | null;
  lawyer: UserRead | null;
  client: Client;
  employment_status: TextChoiceListField;
  referrer: string;
  referrer_type: TextChoiceField;
  tenancy: Tenancy;
  weekly_rent: number | null;
  annual_income_range?: TextChoiceField;
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
export type ClientCreate = {
  first_name: string;
  last_name: string;
  email: string;
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
export type TenancyCreate = {
  address: string;
  suburb: string | null;
  postcode: string | null;
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
  annual_income_range?: string | null;
  referrer?: string;
  referrer_type?: string;
  weekly_rent?: number | null;
};
export type IssueNoteCreator = {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  full_name: string;
  url: string;
};
export type IssueNote = {
  id: number;
  note_type: string;
  text: string;
  event: string | null;
  creator: IssueNoteCreator;
  text_display: string;
  created_at: string;
  reviewee: User | null;
};
export type IssueNoteRead = {
  id: number;
  note_type: string;
  text: string;
  event: string | null;
  creator: IssueNoteCreator;
  text_display: string;
  created_at: string;
  reviewee: UserRead | null;
};
export type IssueUpdate = {
  topic?: string;
  stage?: string;
  is_open?: boolean;
  outcome?: string | null;
  outcome_notes?: string;
  provided_legal_services?: boolean;
  paralegal_id?: number | null;
  lawyer_id?: number | null;
  support_worker_id?: number | null;
  weekly_rent?: number | null;
  employment_status?: string;
  annual_income_range?: string | null;
  referrer?: string;
  referrer_type?: string;
};
export type IssueNoteCreate = {
  note_type: string;
  text: string;
  event?: string | null;
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
export type Service = {
  id: number;
  issue_id: string;
  category: ServiceCategory;
  type: ServiceTypeDiscrete | ServiceTypeOngoing;
  started_at: string;
  finished_at: string | null;
  count: number | null;
  notes: string | null;
};
export type ServiceCreate = {
  category: ServiceCategory;
  type: ServiceTypeDiscrete | ServiceTypeOngoing;
  started_at: string;
  finished_at: string | null;
  count: number | null;
  notes: string | null;
};
export type ServiceUpdate = {
  category?: ServiceCategory;
  type?: ServiceTypeDiscrete | ServiceTypeOngoing;
  started_at?: string;
  finished_at?: string | null;
  count?: number | null;
  notes?: string | null;
};
export type EmailCreate = {
  to_address: string;
  cc_addresses: string[];
  subject: string;
  text: string;
  html: string;
  state?: string;
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
  issue: string;
  from_address: string;
  created_at: string;
  processed_at: string | null;
  sender: User;
  state: string;
  reply_url: string;
  edit_url: string;
  attachments: EmailAttachment[];
};
export type EmailRead = EmailCreate & {
  id: number;
  issue: string;
  from_address: string;
  created_at: string;
  processed_at: string | null;
  sender: UserRead;
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
export type EmailThreadRead = {
  emails: EmailRead[];
  subject: string;
  slug: string;
  most_recent: string;
  url: string;
};
export type EmailUpdate = {
  to_address?: string;
  cc_addresses?: string[];
  subject?: string;
  text?: string;
  html?: string;
  state?: string;
};
export type EmailAttachmentCreate = {
  file: Blob;
};
export type IssueNoteType =
  | "CONFLICT_CHECK_FAILURE"
  | "CONFLICT_CHECK_SUCCESS"
  | "ELIGIBILITY_CHECK_FAILURE"
  | "ELIGIBILITY_CHECK_SUCCESS"
  | "EMAIL"
  | "EVENT"
  | "PARALEGAL"
  | "PERFORMANCE"
  | "REVIEW";
export type PersonCreate = PersonBase & {
  email?: string;
  address?: string;
  phone_number?: string;
  support_contact_preferences?: string;
};
export type IssueDateType =
  | "FILING_DEADLINE"
  | "HEARING_LISTED"
  | "LIMITATION"
  | "NTV_TERMINATION"
  | "OTHER";
export type IssueDateHearingType = "IN_PERSON" | "VIRTUAL";
export type IssueDate = {
  id: number;
  type: IssueDateType;
  date: string;
  hearing_type?: IssueDateHearingType;
  hearing_location?: string;
  issue: Issue;
  notes: string;
  is_reviewed: boolean;
};
export type IssueDateRead = {
  id: number;
  type: IssueDateType;
  date: string;
  hearing_type?: IssueDateHearingType;
  hearing_location?: string;
  issue: IssueRead;
  notes: string;
  is_reviewed: boolean;
};
export type IssueDateCreate = {
  type: IssueDateType;
  date: string;
  issue_id: string;
  hearing_type?: IssueDateHearingType;
  hearing_location?: string;
  notes?: string;
  is_reviewed?: boolean;
};
export type IssueDateUpdate = {
  type?: IssueDateType;
  date?: string;
  issue_id?: string;
  hearing_type?: IssueDateHearingType;
  hearing_location?: string;
  notes?: string;
  is_reviewed?: boolean;
};
export type TenancyUpdate = {
  address?: string;
  suburb?: string | null;
  postcode?: string | null;
  started?: string | null;
  is_on_lease?: string;
  rental_circumstances?: string;
  landlord_id?: number | null;
  agent_id?: number | null;
};
export type ClientUpdate = {
  first_name?: string;
  last_name?: string;
  email?: string;
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
export type UserCreate = {
  first_name: string;
  last_name: string;
  email: string;
  groups: string[];
};
export type UserCreateRead = {
  first_name: string;
  last_name: string;
  email: string;
  url: string;
  groups: string[];
};
export type UserUpdate = {
  first_name?: string;
  last_name?: string;
  email?: string;
  groups?: string[];
};
export type UserUpdateRead = {
  first_name?: string;
  last_name?: string;
  email?: string;
  url?: string;
  groups?: string[];
};
export type MicrosoftUserPermissions = {
  access_level: "FULL_ACCESS" | "PARTIAL_ACCESS" | "NO_ACCESS";
  issues_with_access: Issue[];
  issues_without_access: Issue[];
};
export type MicrosoftUserPermissionsRead = {
  access_level: "FULL_ACCESS" | "PARTIAL_ACCESS" | "NO_ACCESS";
  issues_with_access: IssueRead[];
  issues_without_access: IssueRead[];
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
  useGetNotesQuery,
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
  useGetUserQuery,
  useUpdateUserMutation,
  useGetUserAccountPermissionsQuery,
  useResyncUserAccountPermissionsMutation,
  useGetPotentialUsersQuery,
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
