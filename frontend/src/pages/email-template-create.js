import React from 'react'
import { Formik } from 'formik'
import { Container, Header } from 'semantic-ui-react'

import { mount } from 'utils'
import { api } from 'api'
import { EmailTemplateForm } from 'forms/email-template'

const CONTEXT = window.REACT_CONTEXT

const App = () => (
  <Container>
    <Header as="h1">Create a new email template</Header>
    <Formik
      initialValues={{
        topic: '',
        name: '',
        subject: '',
        text: '',
        html: '',
      }}
      validate={(values) => {}}
      onSubmit={(values, { setSubmitting, setErrors }) => {
        api.templates.email.create(values).then(({ resp, data, errors }) => {
          if (resp.status === 400) {
            setErrors(errors)
          } else if (resp.ok) {
            window.location.href = data.url
          }
          setSubmitting(false)
        })
      }}
    >
      {(formik) => (
        <EmailTemplateForm
          formik={formik}
          topicOptions={CONTEXT.topic_options}
          create
          editable
        />
      )}
    </Formik>
  </Container>
)

mount(App)
