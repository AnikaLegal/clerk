# SharePoint Integration

We use SharePoint to store and edit documents for our cases. Some example documents include:

- Consent forms that we send to the client
- Templated advice for the client
- Templated letters to the landlord

All relevant code lives in the `microsoft` application.
In general we want each case's documents to be stored with [principle of least privilege](https://en.wikipedia.org/wiki/Principle_of_least_privilege) access.

## Environments

We have three Active Directory groups (dev, staging, prod), each with its own SharePoint site/filesystem. Access to one group/site does not grant access to others. Environment access is controlled at the user level by group and folder level permissions (see access section) and at the application level by these two settings:

- `MS_GRAPH_GROUP_ID`: The id of the Active Directory group, used to manage permissions
- `MS_GRAPH_DRIVE_ID`: The id of the SharePoint drive created for the AD group

and these two secrets (envars):

- `AZURE_AD_CLIENT_ID`
- `AZURE_AD_CLIENT_SECRET`

To set up a new environment you need to create a new group in [MS Azure Active Directory](https://portal.azure.com/#blade/Microsoft_AAD_IAM/GroupsManagementMenuBlade/AllGroups) with group type "Microsoft 365". You will then need to copy the Group's object ID as `MS_GRAPH_GROUP_ID` and determine the group's `MS_GRAPH_DRIVE_ID` by [calling the MS Graph API](https://docs.microsoft.com/en-us/graph/api/drive-get?view=graph-rest-1.0&tabs=http#get-the-document-library-associated-with-a-group) (from the command line).

## Filesystem

Documents are stored in each SharePoint site as follows. Case folders are the case id as stored in Clerk.
When a case is created in Clerk the system will create the case folder and copy the relevant template documents into the new case folder.

```
.
├── templates
|   ├── bonds               bonds templates
|   ├── repairs             repairs templates
|   └── evictions           evictions templates
└── cases
    ├── 83457d7d-5875-...   a case
    └── f4d5b5a2-c686-...   another case
```

## Access control

Paralegals are only given read/write access only to the folders of the cases that they are working on. This access is added/removed when they are added/removed from a case.

When users become coordinators, admins or superusers they join the group as "owners", giving them full access permissions to the SharePoint file system in the environment. These permissions are removed if this access is retracted.

## User accounts

New users are automatically assigned an [Office 365 E1 License](https://www.microsoft.com/en-au/microsoft-365/enterprise/office-365-e1) when they first sign in.

## Document Backup

If a user or script accidentally deletes documents from our Group filesystem, there are several safety nets built into Sharepoint Online:

- When an item (i.e. case folder) is deleted from the Group (site) filesystem, it is placed in the first stage recycle bin for 93 days (3 months).
- If the item is deleted from the first stage recycle bin, it is placed in the second stage recycle bin (which appears to be only accessible to Group Owners) where it stays for the remainder of the 93 days.
- Inside the second stage recycle bin, once the 93 days elapse or the item is deleted again, then that item is usually permanently gone.
- However Sharepoint Online creates a backup every 12 hours and keeps it for 14 days, so if the item has been deleted from both recycle bins, it can still be retrieved using File Restore or by contacting Microsoft within the 14 days.
- Please consult this [link](https://docs.microsoft.com/en-us/answers/questions/348043/back-up-and-restore-in-sharepoint-online.html) to Microsoft Q&A for additional details and links to official documents.
- Furthermore, even if the Group (site) itself is deleted using Azure Portal, it can be restored within 30 days.
