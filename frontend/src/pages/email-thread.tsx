import React from 'react'
import { Container, Header, Label } from 'semantic-ui-react'
import styled from 'styled-components'
import { useSnackbar } from 'notistack'
import { mount, getAPIErrorMessage } from 'utils'
import {
  useGetCaseQuery,
  useGetEmailThreadsQuery,
  useUploadEmailAttachmentToSharepointMutation,
  Email,
  Issue,
  EmailAttachment,
} from 'api'
import { UserPermission } from 'types/global'

interface DjangoContext {
  case_pk: string
  thread_slug: string
  case_email_list_url: string
  user: UserPermission
}

const { case_pk, thread_slug, case_email_list_url, user } = (window as any)
  .REACT_CONTEXT as DjangoContext

const App = () => {
  const { enqueueSnackbar } = useSnackbar()
  const [loadingAttachment, setLoadingAttachment] = React.useState<
    number | null
  >(null)
  const [upload] = useUploadEmailAttachmentToSharepointMutation()
  const caseResult = useGetCaseQuery({ id: case_pk })
  const threadResult = useGetEmailThreadsQuery({
    id: case_pk,
    slug: thread_slug,
  })
  const isInitialLoad = caseResult.isLoading || threadResult.isLoading
  if (isInitialLoad) return null

  const issue = caseResult.data!.issue
  const emailThreads = threadResult.data
  const emailThread = emailThreads[0] // Assume a single result
  const { emails } = emailThread

  const onEmailAttachUpload = (emailId: number, attachmentId: number) => () => {
    setLoadingAttachment(attachmentId)
    upload({ id: case_pk, emailId, attachmentId })
      .unwrap()
      .then(() => {
        setLoadingAttachment(null)
      })
      .catch((err) => {
        enqueueSnackbar(
          getAPIErrorMessage(err, 'Failed to upload attachment'),
          {
            variant: 'error',
          }
        )
        setLoadingAttachment(null)
      })
  }

  return (
    <Container>
      <Header as="h1">
        {emailThread.subject}{' '}
        <span style={{ color: 'var(--grey-2)' }}>({issue.fileref})</span>
        <Header.Subheader>
          Most recent emails are at the top
          <br />
          <a href={case_email_list_url}>Back to case emails</a>
        </Header.Subheader>
      </Header>
      <EmailList>
        {emails.map((email) => (
          <EmailItem
            key={email.id}
            email={email}
            issue={issue}
            onEmailAttachUpload={onEmailAttachUpload}
            loadingAttachment={loadingAttachment}
          />
        ))}
      </EmailList>
    </Container>
  )
}

interface EmailItemProps {
  email: Email
  issue: Issue
  onEmailAttachUpload: (emailId: number, attachId: number) => () => void
  loadingAttachment: number | null
}

const EmailItem: React.FC<EmailItemProps> = ({
  email,
  issue,
  onEmailAttachUpload,
  loadingAttachment,
}) => {
  return (
    <EmailContainer key={email.id} state={email.state}>
      <EmailHeader state={email.state}>
        {user.is_admin_or_better && (
          <p>
            <a href={`/admin/emails/email/${email.id}/change/`}>Admin link</a>
          </p>
        )}
        <p>
          <strong>To:</strong>&nbsp;
          {email.to_address}
        </p>
        <p>
          <strong>From:</strong>&nbsp;
          {email.from_address}
        </p>
        {email.cc_addresses.length > 0 && (
          <p>
            <strong>CC:</strong>&nbsp;
            {email.cc_addresses.join(', ')}
          </p>
        )}
        {email.state == 'DRAFT' && <div className="label">Draft</div>}
        {email.state == 'SENT' && (
          <div className="label">
            Sent on {email.processed_at}{' '}
            {email.sender ? `by ${email.sender.full_name}` : null}
          </div>
        )}
        {email.state == 'DELIVERED' && (
          <div className="label">
            Delivered after {email.processed_at}
            {email.sender ? `, sent by ${email.sender.full_name}` : null}
          </div>
        )}
        {email.state == 'DELIVERY_FAILURE' && (
          <div className="label">
            Deilivery failed after {email.processed_at}
            {email.sender ? `, sent by ${email.sender.full_name}` : null}
          </div>
        )}
        {email.state == 'INGESTED' && (
          <div className="label">Received on {email.created_at}</div>
        )}
        {email.state == 'READY_TO_SEND' && (
          <div className="label">Sending...</div>
        )}
      </EmailHeader>
      <EmailBody dangerouslySetInnerHTML={{ __html: email.html }} />
      <EmailControls>
        {email.state == 'DRAFT' ? (
          <a href={email.edit_url} className="header" target="_blank">
            <button className="ui button primary">Edit Draft</button>
          </a>
        ) : (
          <a href={email.reply_url} className="header" target="_blank">
            <button className="ui button">Reply</button>
          </a>
        )}
      </EmailControls>
      {email.attachments.length > 0 && (
        <EmailAttachmentBlock received={email.state == 'INGESTED'}>
          <h5>Attached files</h5>
          <EmailAttachmentList>
            {email.attachments.map((a) => (
              <Attachment
                isUploadEnabled={issue.is_sharepoint_set_up}
                onUpload={onEmailAttachUpload}
                emailId={email.id}
                attachment={a}
                loadingAttachment={loadingAttachment}
                key={a.id}
              />
            ))}
          </EmailAttachmentList>
        </EmailAttachmentBlock>
      )}
    </EmailContainer>
  )
}

interface AttachmentProps {
  emailId: number
  isUploadEnabled: boolean
  onUpload: (emailId: number, attachId: number) => () => void
  attachment: EmailAttachment
  loadingAttachment: number | null
}

const Attachment: React.FC<AttachmentProps> = ({
  emailId,
  onUpload,
  isUploadEnabled,
  attachment: { id, url, name, sharepoint_state },
  loadingAttachment,
}) => {
  const filename = name.split('/').pop()
  const isAnyUploading = !!loadingAttachment
  const isThisUploading = loadingAttachment === id
  const isUploaded = sharepoint_state === 'UPLOADED'

  return (
    <AttachmentEl>
      <a href={url}>{filename}</a>{' '}
      {isUploadEnabled && (
        <>
          {!isUploaded && !isAnyUploading && (
            <Label onClick={onUpload(emailId, id)}>save to sharepoint</Label>
          )}
          {!isUploaded && isAnyUploading && !isThisUploading && (
            <Label style={{ cursor: 'not-allowed' }}>save to sharepoint</Label>
          )}
          {!isUploaded && isAnyUploading && isThisUploading && (
            <Label>saving...</Label>
          )}
          {isUploaded && (
            <Label color="teal" style={{ cursor: 'not-allowed' }}>
              saved to sharepoint
            </Label>
          )}
        </>
      )}
    </AttachmentEl>
  )
}

const EmailList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  margin-top: 1.5rem;
`

const EmailContainer = styled.div`
  border: 6px solid var(--grey);
  box-shadow: 1px 1px 5px -2px #999;

  ${({ state }) => {
    if (state === 'INGESTED') {
      return `border-color: var(--gold-light);`
    } else if (state === 'DELIVERY_FAILURE') {
      return `border-color: var(--peach);`
    }
  }}
`
const EmailHeader = styled.div`
  padding: 1rem;
  background-color: var(--grey);
  border-bottom: solid 1px var(--grey);
  ${({ state }) => {
    if (state === 'INGESTED') {
      return `
    background-color: var(--gold-light);
    border-color: var(--gold-light);
  `
    } else if (state === 'DELIVERY_FAILURE') {
      return `
    background-color: var(--peach);
    border-color: var(--peach);
  `
    }
  }}
  p {
    margin-bottom: 0;
  }
  position: relative;
  .label {
    position: absolute;
    right: 0;
    bottom: 0;
    padding: 1rem;
  }
`
const EmailBody = styled.div`
  padding: 1rem;
  h1,
  h2,
  h3,
  h4,
  h5,
  p,
  div {
    font-size: 1rem !important;
    margin: 0 0 1em;
  }
  blockquote {
    color: var(--dark-6);
    border-left: solid 4px var(--grey);
    padding-left: 1em;
  }
`
const EmailControls = styled.div`
  padding: 0 1rem 1rem 1rem;
`
const EmailAttachmentBlock = styled.div`
  padding: 1rem;
  background-color: var(--grey);
  ${({ received }) =>
    received &&
    `
    background-color: var(--gold-light);
  `}
`
const EmailAttachmentList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.5em;
`

const AttachmentEl = styled.div`
  justify-content: space-between;
  padding: 0.5em;
  align-items: center;
  display: flex;
  background: #fff;
  .ui.label {
    cursor: pointer;
  }
`

mount(App)
