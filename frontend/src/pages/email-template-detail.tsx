import React from 'react'
import { Formik } from 'formik'
import { Container, Header } from 'semantic-ui-react'
import { useSnackbar } from 'notistack'

import { mount, getAPIErrorMessage, getAPIFormErrors } from 'utils'
import { EmailTemplateForm } from 'forms/email-template'

import {
  EmailTemplate,
  useUpdateEmailTemplateMutation,
  useDeleteEmailTemplateMutation,
} from 'api'

interface DjangoContext {
  topic_options: { key: string; value: string; text: string }[]
  template: EmailTemplate
  template_list_url: string
  editable: boolean
}

const CONTEXT = (window as any).REACT_CONTEXT as DjangoContext

const App = () => {
  const { enqueueSnackbar } = useSnackbar()
  const [updateEmailTemplate] = useUpdateEmailTemplateMutation()
  const [deleteEmailTemplate] = useDeleteEmailTemplateMutation()
  const handleDelete = (e) => {
    e.preventDefault()
    if (window.confirm('Are you sure you want to delete this template?')) {
      deleteEmailTemplate({ id: CONTEXT.template.id })
        .unwrap()
        .then(() => {
          window.location.href = CONTEXT.template_list_url
        })
        .catch((err) => {
          enqueueSnackbar(
            getAPIErrorMessage(err, 'Failed to delete this email template'),
            {
              variant: 'error',
            }
          )
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
          updateEmailTemplate({
            id: CONTEXT.template.id,
            emailTemplateCreate: values,
          })
            .unwrap()
            .then(() => {
              enqueueSnackbar('Updated email template', { variant: 'success' })
              setSubmitting(false)
            })
            .catch((err) => {
              enqueueSnackbar(
                getAPIErrorMessage(err, 'Failed to update email template'),
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
