import React from 'react'
import { Formik } from 'formik'
import {
  Container,
  Header,
  Tab,
  Form,
  Button,
  Input,
  Dropdown,
  Checkbox,
  Icon,
  List,
  Label,
} from 'semantic-ui-react'
import * as Yup from 'yup'
import styled from 'styled-components'
import { useSnackbar } from 'notistack'

import { FormErrors } from 'comps/auto-form'
import { mount, getAPIErrorMessage, getAPIFormErrors } from 'utils'
import { MarkdownEditor } from 'comps/markdown-editor'
import {
  useUpdateEmailMutation,
  useDeleteEmailMutation,
  useCreateEmailAttachmentMutation,
  useDownloadEmailAttachmentFromSharepointMutation,
  useDeleteEmailAttachmentMutation,
  useGetCaseQuery,
  useGetCaseDocumentsQuery,
  useGetEmailQuery,
  EmailAttachment,
} from 'api'

interface DjangoContext {
  case_pk: string
  email_pk: number
  case_email_url: string
  email_preview_url: string
}

const { case_pk, email_pk, case_email_url, email_preview_url } = (window as any)
  .REACT_CONTEXT as DjangoContext

const App = () => {
  const { enqueueSnackbar } = useSnackbar()
  const [updateEmail] = useUpdateEmailMutation()
  const [deleteEmail] = useDeleteEmailMutation()
  const [deleteAttachment] = useDeleteEmailAttachmentMutation()

  const caseResult = useGetCaseQuery({ id: case_pk })
  const emailResult = useGetEmailQuery({ id: case_pk, emailId: email_pk })
  const isInitialLoad = caseResult.isLoading || emailResult.isLoading
  if (isInitialLoad) return null

  const issue = caseResult.data!.issue
  const email = emailResult.data
  const { attachments } = email

  const onDeleteAttachment = (attachmentId: number) => () => {
    const confirmed = confirm('Delete this attachment?')
    if (!confirmed) return
    deleteAttachment({ id: case_pk, emailId: email_pk, attachmentId })
      .unwrap()
      .then(() => {
        enqueueSnackbar('Attachment deleted', { variant: 'success' })
      })
      .catch((err) => {
        enqueueSnackbar(
          getAPIErrorMessage(err, 'Failed to delete attachment'),
          {
            variant: 'error',
          }
        )
      })
  }
  const onSubmit = async (values, { setSubmitting, setErrors }) => {
    setSubmitting(true)
    const ccAddresses = values.cc_addresses
      .split(',')
      .map((s) => s.trim())
      .filter((s) => s)
    const requestData = { ...values, cc_addresses: ccAddresses }
    delete requestData.send
    if (values.send) {
      // Send the email
      const confirmed = confirm('Send this email?')
      if (!confirmed) return
      // Mark email for sending.
      requestData.state = 'READY_TO_SEND'
    }
    updateEmail({
      id: case_pk,
      emailId: email_pk,
      emailCreate: requestData,
    })
      .unwrap()
      .then((email) => {
        if (email.state !== 'DRAFT') {
          window.location.href = case_email_url
        } else {
          enqueueSnackbar('Email updated', { variant: 'success' })
          setSubmitting(false)
        }
      })
      .catch((err) => {
        enqueueSnackbar(getAPIErrorMessage(err, 'Failed to update email'), {
          variant: 'error',
        })
        const requestErrors = getAPIFormErrors(err)
        if (requestErrors) {
          setErrors(requestErrors)
        }
        setSubmitting(false)
      })
  }
  const onDelete = (setSubmitting) => {
    const confirmed = confirm('Delete this draft email?')
    if (!confirmed) return
    setSubmitting(true)
    deleteEmail({ id: case_pk, emailId: email_pk })
      .unwrap()
      .then(() => {
        window.location.href = case_email_url
      })
      .catch((err) => {
        enqueueSnackbar(
          getAPIErrorMessage(err, 'Failed to delete this email'),
          {
            variant: 'error',
          }
        )
        setSubmitting(false)
      })
  }
  return (
    <Container>
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-start',
        }}
      >
        <Header as="h1">
          Edit draft email
          <Header.Subheader>
            <a href={case_email_url}>Back to case emails</a>
          </Header.Subheader>
        </Header>
        <Label color="blue">
          Client: {issue.client.full_name} at {issue.client.email}
        </Label>
      </div>
      <Formik
        initialValues={{
          to_address: email ? email.to_address : '',
          subject: email ? email.subject : '',
          cc_addresses: email ? email.cc_addresses.join(', ') : '',
          text: email ? email.text : '',
          html: email ? email.html : '',
          send: false, // True when sending vs saving draft.
        }}
        validationSchema={Yup.object().shape({
          to_address: Yup.string().email().required('Required'),
          subject: Yup.string().required('Required'),
          cc_addresses: Yup.string(),
          text: Yup.string().required('Required'),
          html: Yup.string(),
        })}
        onSubmit={onSubmit}
      >
        {({
          values,
          errors,
          touched,
          handleChange,
          handleSubmit,
          isSubmitting,
          setFieldValue,
          setSubmitting,
        }) => (
          <Form onSubmit={handleSubmit} error={Object.keys(errors).length > 0}>
            <Form.Field error={touched.subject && !!errors.subject}>
              <label>Subject</label>
              <Input
                value={values.subject}
                name="subject"
                onChange={handleChange}
                disabled={isSubmitting}
                placeholder="A very important email"
              />
            </Form.Field>
            <Form.Field error={touched.to_address && !!errors.to_address}>
              <label>To Address</label>
              <Input
                value={values.to_address}
                name="to_address"
                placeholder="jane@example.com"
                onChange={handleChange}
                disabled={isSubmitting}
              />
            </Form.Field>
            <Form.Field error={touched.cc_addresses && !!errors.cc_addresses}>
              <label>CC Addresses</label>
              <Input
                value={values.cc_addresses}
                name="cc_addresses"
                placeholder="anne@example.com, mark@example.com"
                onChange={handleChange}
                disabled={isSubmitting}
              />
            </Form.Field>
            <MarkdownEditor
              text={values.text}
              html={values.html}
              onChangeText={(text) => setFieldValue('text', text)}
              onChangeHtml={(html) => setFieldValue('html', html)}
              disabled={isSubmitting}
              placeholder="Dear Ms Example..."
            />
            <Form.Field>
              <Checkbox
                toggle
                label="Ready to send"
                onChange={(e, data) => setFieldValue('send', data.checked)}
                checked={values.send}
              />
            </Form.Field>
            <FormErrors errors={errors} touched={touched} />
            {values.send && (
              <Button
                primary
                icon
                labelPosition="left"
                type="submit"
                disabled={isSubmitting}
                loading={isSubmitting}
              >
                <Icon name="mail" />
                Send
              </Button>
            )}
            {!values.send && (
              <Button
                icon
                labelPosition="left"
                type="submit"
                disabled={isSubmitting}
                loading={isSubmitting}
              >
                <Icon name="save" />
                Save
              </Button>
            )}

            <Button
              disabled={isSubmitting}
              loading={isSubmitting}
              href={email_preview_url}
              target="_blank"
            >
              Preview
            </Button>
            <Button
              color="red"
              disabled={isSubmitting}
              loading={isSubmitting}
              onClick={() => onDelete(setSubmitting)}
            >
              Delete
            </Button>
          </Form>
        )}
      </Formik>
      <Tab
        panes={[
          {
            menuItem: 'Attach from SharePoint',
            render: () => (
              <Tab.Pane>
                <SharepoinAttachForm />
              </Tab.Pane>
            ),
          },
          {
            menuItem: 'Upload attachment',
            render: () => (
              <Tab.Pane>
                <FileUploadAttachForm />
              </Tab.Pane>
            ),
          },
        ]}
      />
      {attachments.length === 0 && (
        <p style={{ opacity: 0.7 }}>
          No files are currently attached to this email
        </p>
      )}
      {attachments.length > 0 && (
        <List celled>
          {attachments.map((a) => (
            <Attachment
              key={a.id}
              attachment={a}
              onDelete={onDeleteAttachment}
            />
          ))}
        </List>
      )}
    </Container>
  )
}

interface AttachmentProps {
  attachment: EmailAttachment
  onDelete: (attachmentId: number) => () => void
}

const Attachment: React.FC<AttachmentProps> = ({ attachment, onDelete }) => {
  return (
    <List.Item>
      <List.Content floated="right">
        <Button onClick={onDelete(attachment.id)}>Delete</Button>
      </List.Content>
      <List.Header as="a" href={attachment.url}>
        {attachment.name.split('/').slice(-1)}
      </List.Header>
      <List.Description>{attachment.content_type}</List.Description>
    </List.Item>
  )
}

const FileUploadAttachForm = () => {
  const [createAttachment] = useCreateEmailAttachmentMutation()
  const { enqueueSnackbar } = useSnackbar()
  return (
    <Formik
      initialValues={{ file: null }}
      validationSchema={Yup.object().shape({
        file: Yup.mixed<File>()
          .test('file-required', 'Please select a file', (file) =>
            Boolean(file)
          )
          .test('file-size', 'File size must be no greater than 30MB', (file) =>
            file ? file.size / 1024 / 1024 <= 30 : true
          ),
      })}
      onSubmit={(values, { setSubmitting, setErrors }) => {
        setSubmitting(true)
        const form = new FormData()
        form.append('file', values.file)
        createAttachment({
          id: case_pk,
          emailId: email_pk,
          emailAttachmentCreate: form as any,
        })
          .unwrap()
          .then(() => {
            enqueueSnackbar('Uploaded file', { variant: 'success' })
            setSubmitting(false)
          })
          .catch((err) => {
            enqueueSnackbar(getAPIErrorMessage(err, 'Failed to upload file'), {
              variant: 'error',
            })
            const requestErrors = getAPIFormErrors(err)
            if (requestErrors) {
              setErrors(requestErrors)
            }
            setSubmitting(false)
          })
      }}
    >
      {({ errors, touched, handleSubmit, isSubmitting, setFieldValue }) => (
        <Form onSubmit={handleSubmit} error={Object.keys(errors).length > 0}>
          <AttachFormGroup>
            <Form.Field error={touched.file && !!errors.file}>
              <Input
                type="file"
                name="file"
                disabled={isSubmitting}
                onChange={(event) => {
                  if (!event.currentTarget.files) return
                  const files = Object.values(event.currentTarget.files).map(
                    (file: File) => file
                  )
                  setFieldValue('file', files[0], true)
                }}
              />
            </Form.Field>
            <Button
              icon
              labelPosition="left"
              disabled={isSubmitting}
              loading={isSubmitting}
              type="submit"
            >
              <Icon name="attach" />
              Attach file
            </Button>
          </AttachFormGroup>
          <FormErrors errors={errors} touched={touched} />
        </Form>
      )}
    </Formik>
  )
}

const SharepoinAttachForm = () => {
  const { enqueueSnackbar } = useSnackbar()
  const docsResult = useGetCaseDocumentsQuery({ id: case_pk })
  const sharePointDocs = (docsResult.data?.documents ?? []).filter(
    (doc) => doc.is_file
  )

  const [downloadAttachment] =
    useDownloadEmailAttachmentFromSharepointMutation()

  const options = sharePointDocs.map((doc) => ({
    key: doc.id,
    value: doc.id,
    description: `${(doc.size / 1024 / 1024).toFixed(2)} MB`,
    text: doc.name,
  }))
  return (
    <Formik
      initialValues={{ sharepointId: '' }}
      validationSchema={Yup.object().shape({
        sharepointId: Yup.string()
          .test('file-required', 'Please select a document', (sharepointId) =>
            Boolean(sharepointId)
          )
          .test(
            'file-size',
            'File size must be no greater than 30MB',
            (sharepointId) => {
              const doc = sharePointDocs.find((d) => d.id === sharepointId)
              if (!doc) {
                return true
              } else {
                return doc.size / 1024 / 1024 <= 30
              }
            }
          ),
      })}
      onSubmit={(values, { setSubmitting, setErrors }) => {
        setSubmitting(true)
        downloadAttachment({
          id: case_pk,
          emailId: email_pk,
          sharepointId: values.sharepointId,
        })
          .unwrap()
          .then(() => {
            enqueueSnackbar('Attached file', { variant: 'success' })
            setSubmitting(false)
          })
          .catch((err) => {
            enqueueSnackbar(getAPIErrorMessage(err, 'Failed to attach file'), {
              variant: 'error',
            })
            const requestErrors = getAPIFormErrors(err)
            if (requestErrors) {
              setErrors(requestErrors)
            }
            setSubmitting(false)
          })
      }}
    >
      {({
        values,
        errors,
        touched,
        handleSubmit,
        isSubmitting,
        setFieldValue,
      }) => (
        <Form onSubmit={handleSubmit} error={Object.keys(errors).length > 0}>
          <AttachFormGroup>
            <Form.Field error={touched.sharepointId && !!errors.sharepointId}>
              <Dropdown
                search
                fluid
                selection
                disabled={isSubmitting}
                loading={docsResult.isLoading}
                placeholder="Select a document"
                options={options}
                onChange={(e, { value }) =>
                  setFieldValue('sharepointId', value, false)
                }
                value={values.sharepointId}
              />
            </Form.Field>
            <Button
              icon
              labelPosition="left"
              disabled={isSubmitting}
              loading={isSubmitting}
              type="submit"
            >
              <Icon name="attach" />
              Attach file
            </Button>
          </AttachFormGroup>
          <FormErrors errors={errors} touched={touched} />
        </Form>
      )}
    </Formik>
  )
}

const AttachFormGroup = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1em;
  .field {
    flex-grow: 1;
    margin: 0 !important;
  }
`

mount(App)
