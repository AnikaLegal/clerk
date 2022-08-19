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
  Icon,
  List,
  Message,
  Label,
} from 'semantic-ui-react'
import * as Yup from 'yup'

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
  const onDeleteAttachment = (attachId) => {
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
  const onSend = () => {
    const confirmed = confirm(
      'Send this email? Remember to save any changes before sending.'
    )
    if (!confirmed) return
    api.email.send(issue.id, email.id).then(({ resp, data }) => {
      if (resp.ok) {
        window.location = case_email_url
      }
    })
  }
  const onDelete = () => {
    const confirmed = confirm('Delete this draft email?')
    if (!confirmed) return
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
        }}
        validationSchema={Yup.object().shape({
          to_address: Yup.string().email().required('Required'),
          subject: Yup.string().required('Required'),
          cc_addresses: Yup.string(),
          text: Yup.string().required('Required'),
          html: Yup.string(),
        })}
        onSubmit={(values, { setSubmitting, setErrors }) => {
          setSubmitting(true)
          const ccAddresses = values.cc_addresses
            .split(',')
            .map((s) => s.trim())
            .filter((s) => s)
          const requestData = { ...values, cc_addresses: ccAddresses }
          api.email
            .update(issue.id, email.id, requestData)
            .then(({ resp, data }) => {
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
            <FormErrors errors={errors} touched={touched} />
            <Button
              primary
              icon
              labelPosition="left"
              disabled={isSubmitting}
              loading={isSubmitting}
              onClick={() => setSubmitting(true) || onSend()}
            >
              <Icon name="mail" />
              Send email
            </Button>
            <Button
              type="submit"
              disabled={isSubmitting}
              loading={isSubmitting}
            >
              Save draft
            </Button>
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
              onClick={() => setSubmitting(true) || onDelete()}
            >
              Delete
            </Button>
          </Form>
        )}
      </Formik>
      <Tab
        panes={[
          {
            menuItem: 'Upload attachment',
            render: () => (
              <Tab.Pane>
                <FileUploadAttachForm onUploadAttachment={onUploadAttachment} />
              </Tab.Pane>
            ),
          },
          {
            menuItem: 'Attach from SharePoint',
            render: () => (
              <Tab.Pane>
                <SharepoinAttachForm onAttachSharepoint={onAttachSharepoint} />
              </Tab.Pane>
            ),
          },
        ]}
      />
      <List celled>
        {attachments.map((a) => (
          <List.Item>
            <List.Header as="a">{a.name}</List.Header>
            {a.content_type}
          </List.Item>
        ))}
      </List>
    </Container>
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
      const attachment = { file: values.file, content_type: values.file.type }
      onUploadAttachment({ attachment }).then(({ resp, data }) => {
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
        <Form.Group inline>
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
        </Form.Group>
        <FormErrors errors={errors} touched={touched} />
      </Form>
    )}
  </Formik>
)

const SharepoinAttachForm = ({ onAttachSharepoint }) => {
  const [isLoading, setIsLoading] = useState(false)
  const onChange = (e) => {
    debugger
    onUploadAttachment
  }
  return <Input type="file" disabled={isLoading} onChange={onChange} />
}
mount(App)
