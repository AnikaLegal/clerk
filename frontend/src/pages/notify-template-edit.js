import React, { useState } from 'react'
import { Formik } from 'formik'
import { Container, Header } from 'semantic-ui-react'

import { mount } from 'utils'
import { api } from 'api'

import { NotifyTemplateForm } from 'forms/notify-template'

const { template, notify_template_url } = window.REACT_CONTEXT

const App = () => {
  const onDelete = (e) => {
    e.preventDefault()
    const isDelete = confirm(
      'Are you sure you want to delete this notification?'
    )
    if (!isDelete) return
    api.templates.notify.delete(template.id).then(({ resp, data }) => {
      window.location.href = notify_template_url
    })
  }
  return (
    <Container>
      <Header as="h1">
        Edit notification template
        <Header.Subheader>
          <a href={notify_template_url}>Back to notification templates</a>
        </Header.Subheader>
      </Header>
      <Formik
        initialValues={getTemplateValues(template)}
        validate={(values) => {}}
        onSubmit={(values, { setSubmitting, setErrors, resetForm }) => {
          let update_data = values
          if (!values.event) {
            update_data = { ...values, event_stage: '' }
          }
          api.templates.notify
            .update(template.id, update_data)
            .then(({ resp, data }) => {
              if (resp.status === 400) {
                setErrors(data)
              } else if (resp.ok) {
                resetForm({ values: getTemplateValues(data) })
              }
              setSubmitting(false)
            })
        }}
      >
        {(formik) => <NotifyTemplateForm formik={formik} onDelete={onDelete} />}
      </Formik>
    </Container>
  )
}
const getTemplateValues = (template) => ({
  name: template.name,
  topic: template.topic,
  event: template.event.value,
  event_stage: template.event_stage,
  channel: template.channel.value,
  target: template.target.value,
  raw_text: template.raw_text,
  message_text: template.message_text,
})

mount(App)
