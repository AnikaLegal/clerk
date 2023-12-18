import React from 'react'
import { Formik } from 'formik'
import { Container, Header } from 'semantic-ui-react'
import { useSnackbar } from 'notistack'

import { mount, getAPIErrorMessage, getAPIFormErrors } from 'utils'
import { NotifyTemplateForm } from 'forms/notify-template'
import { useCreateNotificationTemplateMutation } from 'apiNew'

interface DjangoContext {
  topic_options: { key: string; value: string; text: string }[]
}

const CONTEXT = (window as any).REACT_CONTEXT as DjangoContext

const App = () => {
  const [createNotifyTemplate] = useCreateNotificationTemplateMutation()
  const { enqueueSnackbar } = useSnackbar()

  return (
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
          let createData = values
          if (!values.event) {
            createData = { ...values, event_stage: '' }
          }
          createNotifyTemplate({ notificationTemplateCreate: createData })
            .unwrap()
            .then((template) => {
              window.location.href = template.url
            })
            .catch((err) => {
              enqueueSnackbar(
                getAPIErrorMessage(
                  err,
                  'Failed to create a new notification template'
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
            topicOptions={CONTEXT.topic_options}
            create
          />
        )}
      </Formik>
    </Container>
  )
}

mount(App)
