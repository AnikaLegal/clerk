import React from 'react'
import { Formik } from 'formik'
import { Container, Header } from 'semantic-ui-react'

import { mount } from 'utils'
import { api } from 'api'
import { EmailTemplateForm } from 'forms/email-template'

const CONTEXT = window.REACT_CONTEXT

const App = () => {
  const handleDelete = (e) => {
    e.preventDefault()
    if (window.confirm('Are you sure you want to delete this template?')) {
      api.templates.email.delete(CONTEXT.template.id).then(() => {
        window.location.href = CONTEXT.template_list_url
      })
    }
  }
  return (
    <Container>
      <Header as="h1">Email template</Header>
      <Formik
        initialValues={{
          topic: CONTEXT.template.topic,
          name: CONTEXT.template.name,
          subject: CONTEXT.template.subject,
          text: CONTEXT.template.text,
          html: '',
        }}
        validate={(values) => {}}
        onSubmit={(values, { setSubmitting, setErrors }) => {
          api.templates.email
            .update(CONTEXT.template.id, values)
            .then(({ resp, errors }) => {
              if (resp.status === 400) {
                setErrors(errors)
              }
              setSubmitting(false)
            })
        }}
      >
        {(formik) => (
          <EmailTemplateForm
            formik={formik}
            create={false}
            topicOptions={CONTEXT.topic_options}
            editable={CONTEXT.editable}
            handleDelete={handleDelete}
          />
        )}
      </Formik>
    </Container>
  )
}

mount(App)
