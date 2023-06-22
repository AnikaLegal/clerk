import React from 'react'
import { Formik } from 'formik'
import { Container, Header } from 'semantic-ui-react'

import { mount } from 'utils'
import { api } from 'api'

import { NotifyTemplateForm } from 'forms/notify-template'

const CONTEXT = window.REACT_CONTEXT

const App = () => (
  <Container>
    <Header as="h1">Create a new notification template</Header>
    <Formik
      initialValues={{
        name: '',
        topic: '',
        event: 'STAGE_CHANGE',
        event_stage: '',
        channel: 'SLACK',
        target: '',
        raw_text: '',
        message_text: '',
      }}
      validate={(values) => {}}
      onSubmit={(values, { setSubmitting, setErrors }) => {
        let create_data = values
        if (!values.event) {
          create_data = { ...values, event_stage: '' }
        }
        api.templates.notify.create(create_data).then(({ resp, data, errors }) => {
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
        <NotifyTemplateForm
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
