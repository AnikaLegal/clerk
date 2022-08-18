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
  Message,
  Label,
  Segment,
} from 'semantic-ui-react'
import * as Yup from 'yup'

import { mount } from 'utils'
import { api } from 'api'
import { MarkdownEditor } from 'comps/markdown-editor'

const { issue, case_email_url, email, sharepoint_docs, email_preview_url } =
  window.REACT_CONTEXT

const App = () => {
  const onUploadAttachment = () => {}
  const onAttachSharepoint = () => {}
  const onDeleteAttachment = () => {}
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
          to_address: email ? email.from_address : '',
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
          html: Yup.string().required('Required'),
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
            {Object.entries(errors).map(
              ([k, v]) =>
                touched[k] && (
                  <div key={k} className="ui error message">
                    <div className="header">{k}</div>
                    <p>{v}</p>
                  </div>
                )
            )}
            {/* Email attachments */}
            <Button
              primary
              disabled={isSubmitting}
              loading={isSubmitting}
              onClick={() => setSubmitting(true) || onSend()}
            >
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
    </Container>
  )
}

mount(App)
