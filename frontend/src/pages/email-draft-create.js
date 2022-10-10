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
  Label,
  Segment,
} from 'semantic-ui-react'
import * as Yup from 'yup'

import { mount, MarkdownAsHtmlDisplay, markdownToHtml } from 'utils'
import { api } from 'api'

const { templates, issue, parent_email, case_email_url } = window.REACT_CONTEXT

const App = () => {
  const onSubmit = (values, { setSubmitting, setErrors }) => {
    setSubmitting(true)
    const requestData = {
      ...values,
      html: markdownToHtml(values.text),
    }
    api.email.create(issue.id, requestData).then(({ resp, data }) => {
      if (resp.status === 400) {
        setErrors(data)
        setSubmitting(false)
      } else if (resp.ok) {
        window.location.href = data.edit_url
      } else {
        setSubmitting(false)
      }
    })
  }
  const panes = [
    {
      menuItem: 'Template',
      render: () => (
        <Tab.Pane attached={false}>
          <TemplateForm
            templates={templates}
            onSubmit={onSubmit}
            parent_email={parent_email}
          />
        </Tab.Pane>
      ),
    },
    {
      menuItem: 'Custom',
      render: () => (
        <Tab.Pane attached={false}>
          <CustomDraftForm onSubmit={onSubmit} parent_email={parent_email} />
        </Tab.Pane>
      ),
    },
  ]
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
          Create a new draft email
          <Header.Subheader>
            <a href={case_email_url}>Back to case emails</a>
          </Header.Subheader>
        </Header>
        <Label color="blue">
          Client: {issue.client.full_name} at {issue.client.email}
        </Label>
      </div>
      {parent_email && (
        <Segment secondary>
          Replying to <strong>{parent_email.subject}</strong> from{' '}
          {parent_email.from_address}
        </Segment>
      )}
      <Tab menu={{ pointing: true }} panes={panes} />
    </Container>
  )
}

const TemplateForm = ({ templates, onSubmit, parent_email }) => {
  const [templateId, setTemplateId] = useState(null)
  const templateOptions = templates.map((t) => ({
    key: t.id,
    text: t.name,
    value: t.id,
  }))
  const template = templates.find((t) => t.id === templateId)
  return (
    <>
      <Dropdown
        fluid
        selection
        style={{ marginBottom: '1em' }}
        value={templateId}
        placeholder="Select an email template"
        options={templateOptions}
        onChange={(e, { value }) => setTemplateId(value)}
      />
      {template && (
        <Formik
          key={templateId}
          initialValues={{
            to_address: parent_email ? parent_email.from_address : '',
            subject: parent_email ? parent_email.subject : template.subject,
            text: template.text,
          }}
          validationSchema={Yup.object().shape({
            to_address: Yup.string().email().required('Required'),
            subject: Yup.string().required('Required'),
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
          }) => (
            <Form
              onSubmit={handleSubmit}
              error={Object.keys(errors).length > 0}
            >
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
              <Form.Field error={touched.subject && !!errors.subject}>
                <label>Subject</label>
                <Input
                  value={values.subject}
                  name="subject"
                  placeholder="A very important email"
                  onChange={handleChange}
                  disabled={isSubmitting}
                />
              </Form.Field>
              <Segment secondary>
                <MarkdownAsHtmlDisplay markdown={template.text} />
              </Segment>
              {Object.entries(errors).map(
                ([k, v]) =>
                  touched[k] && (
                    <div key={k} className="ui error message">
                      <div className="header">{k}</div>
                      <p>{v}</p>
                    </div>
                  )
              )}
              <Button
                primary
                type="submit"
                disabled={isSubmitting}
                loading={isSubmitting}
              >
                Create draft
              </Button>
            </Form>
          )}
        </Formik>
      )}
    </>
  )
}

const CustomDraftForm = ({ onSubmit, parent_email }) => {
  return (
    <Formik
      initialValues={{
        to_address: parent_email ? parent_email.from_address : '',
        subject: parent_email ? parent_email.subject : '',
      }}
      validationSchema={Yup.object().shape({
        to_address: Yup.string().email().required('Required'),
        subject: Yup.string().required('Required'),
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
      }) => (
        <Form onSubmit={handleSubmit} error={Object.keys(errors).length > 0}>
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
          <Form.Field error={touched.subject && !!errors.subject}>
            <label>Subject</label>
            <Input
              value={values.subject}
              name="subject"
              placeholder="A very important email"
              onChange={handleChange}
              disabled={isSubmitting}
            />
          </Form.Field>
          {Object.entries(errors).map(
            ([k, v]) =>
              touched[k] && (
                <div key={k} className="ui error message">
                  <div className="header">{k}</div>
                  <p>{v}</p>
                </div>
              )
          )}
          <Button
            primary
            type="submit"
            disabled={isSubmitting}
            loading={isSubmitting}
          >
            Create draft
          </Button>
        </Form>
      )}
    </Formik>
  )
}

mount(App)
