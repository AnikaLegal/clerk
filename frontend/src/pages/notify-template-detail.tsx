import React from 'react'
import { Formik } from 'formik'
import { Container, Header } from 'semantic-ui-react'
import { useSnackbar } from 'notistack'

import { mount, getAPIErrorMessage, getAPIFormErrors } from 'utils'
import { NotifyTemplateForm } from 'forms/notify-template'
import {
  NotificationTemplate,
  useUpdateNotificationTemplateMutation,
  useDeleteNotificationTemplateMutation,
} from 'api'

interface DjangoContext {
  template: NotificationTemplate
  topic_options: { key: string; value: string; text: string }[]
  notify_template_url: string
}

const { template, topic_options, notify_template_url } = (window as any)
  .REACT_CONTEXT as DjangoContext

const App = () => {
  const { enqueueSnackbar } = useSnackbar()
  const [updateNotificationTemplate] = useUpdateNotificationTemplateMutation()
  const [deleteNotificationTemplate] = useDeleteNotificationTemplateMutation()

  const onDelete = (e) => {
    e.preventDefault()
    const isDelete = confirm(
      'Are you sure you want to delete this notification template?'
    )
    if (!isDelete) return
    deleteNotificationTemplate({ id: template.id })
      .unwrap()
      .then(() => {
        window.location.href = notify_template_url
      })
      .catch((err) => {
        enqueueSnackbar(
          getAPIErrorMessage(
            err,
            'Failed to delete this notification template'
          ),
          {
            variant: 'error',
          }
        )
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
          let updateData = values
          if (!values.event) {
            updateData = { ...values, event_stage: '' }
          }
          updateNotificationTemplate({
            id: template.id,
            notificationTemplateCreate: updateData,
          })
            .unwrap()
            .then(() => {
              enqueueSnackbar('Updated notification template', {
                variant: 'success',
              })
              setSubmitting(false)
            })
            .catch((err) => {
              enqueueSnackbar(
                getAPIErrorMessage(
                  err,
                  'Failed to update notification template'
                ),
                {
                  variant: 'error',
                }
              )
              const requestErrors = getAPIFormErrors(err)
              if (requestErrors) {
                setErrors(requestErrors)
              }
              setSubmitting(false)
            })
        }}
      >
        {(formik) => (
          <NotifyTemplateForm
            formik={formik}
            topicOptions={topic_options}
            onDelete={onDelete}
          />
        )}
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
