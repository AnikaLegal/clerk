import React from 'react'
import { Formik } from 'formik'
import { Container, Header } from 'semantic-ui-react'
import { useSnackbar } from 'notistack'

import { mount, getAPIErrorMessage, getAPIFormErrors } from 'utils'
import { EmailTemplateForm } from 'forms/email-template'
import { useCreateEmailTemplateMutation } from 'apiNew'

interface DjangoContext {
  topic_options: { key: string; value: string; text: string }[]
}

const CONTEXT = (window as any).REACT_CONTEXT as DjangoContext

const App = () => {
  const [createEmailTemplate] = useCreateEmailTemplateMutation()
  const { enqueueSnackbar } = useSnackbar()
  return (
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
          createEmailTemplate({ emailTemplateCreate: values })
            .unwrap()
            .then((template) => {
              window.location.href = template.url
            })
            .catch((err) => {
              enqueueSnackbar(
                getAPIErrorMessage(
                  err,
                  'Failed to create a new email template'
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
          <EmailTemplateForm
            formik={formik}
            topicOptions={CONTEXT.topic_options}
            create
            handleDelete={null}
            editable
          />
        )}
      </Formik>
    </Container>
  )
}
mount(App)
