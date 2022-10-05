import React, { useState } from 'react'
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
  Message,
  Label,
} from 'semantic-ui-react'
import * as Yup from 'yup'
import styled from 'styled-components'

import { FormErrors } from 'comps/auto-form'
import { mount } from 'utils'
import { api } from 'api'
import { MarkdownEditor } from 'comps/markdown-editor'

const { issue, case_email_url, email, sharepoint_docs, email_preview_url } =
  window.REACT_CONTEXT

const App = () => {
  const [attachments, setAttachments] = useState(email.attachments)
  const onUploadAttachment = (attachment) => {
    return api.email.attachment
      .create(issue.id, email.id, attachment)
      .then(({ resp, data }) => {
        if (resp.ok) {
          setAttachments([...attachments, data])
        }
        return { resp, data }
      })
  }
  const onAttachSharepoint = (sharepointId) => {
    return api.email.attachment
      .createFromSharepoint(issue.id, email.id, sharepointId)
      .then(({ resp, data }) => {
        if (resp.ok) {
          setAttachments([...attachments, data])
        }
        return { resp, data }
      })
  }
  const onDeleteAttachment = (attachId) => () => {
    const confirmed = confirm('Delete this attachment?')
    if (!confirmed) return new Promise()
    return api.email.attachment
      .delete(issue.id, email.id, attachId)
      .then(({ resp, data }) => {
        if (resp.ok) {
          setAttachments(attachments.filter((a) => a.id !== attachId))
        }
        return { resp, data }
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
    const { resp, data } = await api.email.update(
      issue.id,
      email.id,
      requestData
    )
    if (resp.status === 400) {
      setErrors(data)
    }
    if (resp.ok && values.send) {
      // Send email
      const confirmed = confirm('Send this email?')
      if (!confirmed) return
      const { resp: sendResp, data: sendData } = await api.email.send(
        issue.id,
        email.id
      )
      if (sendResp.ok) {
        window.location = case_email_url
      }
    }
    setSubmitting(false)
  }
  const onDelete = (setSubmitting) => {
    const confirmed = confirm('Delete this draft email?')
    if (!confirmed) return
    setSubmitting(true)
    api.email.delete(issue.id, email.id).then(({ resp, data }) => {
      if (resp.ok) {
        window.location = case_email_url
      }
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
                <SharepoinAttachForm
                  onAttachSharepoint={onAttachSharepoint}
                  sharePointDocs={sharepoint_docs}
                />
              </Tab.Pane>
            ),
          },
          {
            menuItem: 'Upload attachment',
            render: () => (
              <Tab.Pane>
                <FileUploadAttachForm onUploadAttachment={onUploadAttachment} />
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

const Attachment = ({ attachment, onDelete }) => {
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

const FileUploadAttachForm = ({ onUploadAttachment }) => (
  <Formik
    initialValues={{ file: null }}
    validationSchema={Yup.object().shape({
      file: Yup.mixed()
        .test('file-required', 'Please select a file', (file) => Boolean(file))
        .test('file-size', 'File size must be no greater than 30MB', (file) =>
          file ? file.size / 1024 / 1024 <= 30 : true
        ),
    })}
    onSubmit={(values, { setSubmitting, setErrors }) => {
      setSubmitting(true)
      onUploadAttachment(values).then(({ resp, data }) => {
        if (resp.status === 400) {
          setErrors(data)
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
      setSubmitting,
    }) => (
      <Form onSubmit={handleSubmit} error={Object.keys(errors).length > 0}>
        <AttachFormGroup>
          <Form.Field error={touched.file && !!errors.file}>
            <Input
              type="file"
              name="file"
              disabled={isSubmitting}
              onChange={(e, { name, value }) => {
                setFieldValue('file', e.target.files[0], true)
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

const SharepoinAttachForm = ({ onAttachSharepoint, sharePointDocs }) => {
  const [isLoading, setIsLoading] = useState(false)
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
        onAttachSharepoint(values.sharepointId).then(({ resp, data }) => {
          if (resp.status === 400) {
            setErrors(data)
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
        setSubmitting,
      }) => (
        <Form onSubmit={handleSubmit} error={Object.keys(errors).length > 0}>
          <AttachFormGroup>
            <Form.Field error={touched.sharepointId && !!errors.sharepointId}>
              <Dropdown
                search
                fluid
                selection
                disabled={isSubmitting}
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
