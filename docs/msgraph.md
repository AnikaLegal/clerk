# Microsoft Graph

- MS Graph is an API service offering resources and functionality that spans across all of M365: files, calendar, messaging, tasks, etc.
- We are currently using a small subset of MS Graph for document management on our Clerk Case Management System, all of that logic lives inside the `microsoft` app, and we can build on those foundations to leverage MS Graph to cover further use cases.
- The key concepts (resources) behind MS Graph are Users and Groups: a User corresponds to a Microsoft Account, a Group is a collection of Users having access to the Group's file system - they collaborate with each other and share resources inside the Group.
- Users and Groups can be created and managed from the organisation's Azure Active Directory account, or by making direct API calls to MS Graph.

## Authentication

- We have registered our app on Azure AD with application permissions, and set the specific permissions we need, this returns us two values that we can use to authenticate our app:

```
AZURE_AD_CLIENT_ID
AZURE_AD_CLIENT_SECRET
```

- Our logic uses the `msal` library to authenticate our app with Azure AD and then to obtain the access token to make API calls to MS Graph.

## Document Management

We are using MS Graph to store and manage documents for our Clerk CMS, examples of such documents include:

- Consent forms for the client
- Templated advice for the client
- Templated letters for the landlord

Here is the implementation:

- We have a Group with its own filesystem (drive) holding our documents (folders and files):

```
.
├── templates
|   ├── bonds               bonds templates
|   ├── repairs             repairs templates
|   └── evictions           evictions templates
└── cases
    ├── 83457d7d-5875...   one case
    └── f4d5b5a2-c686...   another case
```

- Currently we have a Group for each of our environments (development, staging, production), each Group is self contained with its own filesystem, Users, and permissions - we use the following values to identify the specific Group and filesystem for our API calls

```
MS_GRAPH_GROUP_ID
MS_GRAPH_DRIVE_ID
```

- We can also manipulate resources in the Group's filesystem with a User Interface; after logging on to office.com, using either SharePoint or OneDrive we can personally manage documents stored in the Group's filesystem.
- The issue of permissions (authorisation) over documents in the Group's filesystem follows the [principle of least privilege](https://en.wikipedia.org/wiki/Principle_of_least_privilege) whereby Users are given enough access to do their job and no more.
- Coordinators are made Group members, giving them read/write access over all the documents in the Group's filesystem; paralegals are not made Group members, they are given read/write access only to the folders corresponding to the cases that they have been assigned.
- When a case is created, a copy of the relevant templates folder is made with the name of the new case and placed in the `cases` folder.
