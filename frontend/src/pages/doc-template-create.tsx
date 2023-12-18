import React from 'react'
import { Formik } from 'formik'
import { Container, Header } from 'semantic-ui-react'
import { useSnackbar } from 'notistack'

import { mount, getAPIErrorMessage, getAPIFormErrors } from 'utils'
import { DocumentTemplateForm } from 'forms/doc-template'
import { useCreateDocumentTemplateMutation } from 'apiNew'

interface DjangoContext {
  list_url: string
  topic_options: { key: string; value: string; text: string }[]
}

const CONTEXT = (window as any).REACT_CONTEXT as DjangoContext

const App = () => {
  const [createDocumentTemplate] = useCreateDocumentTemplateMutation()
  const { enqueueSnackbar } = useSnackbar()
  return (
    <Container>
      <Header as="h1">Create a new document template</Header>
      <Formik
        initialValues={{
          topic: '',
          files: [],
        }}
        validate={(values) => {}}
        onSubmit={(values, { setSubmitting, setErrors }) => {
          const form = new FormData()
          form.append('topic', values.topic)
          for (let f of values.files) {
            form.append('files', f)
          }
          createDocumentTemplate({ documentTemplateCreate: form as any })
            .unwrap()
            .then(() => {
              window.location.href = CONTEXT.list_url
            })
            .catch((err) => {
              enqueueSnackbar(
                getAPIErrorMessage(
                  err,
                  'Failed to create a new document template'
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
          <DocumentTemplateForm
            formik={formik}
            topicOptions={CONTEXT.topic_options}
          />
        )}
      </Formik>
    </Container>
  )
}
mount(App)
