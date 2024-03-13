import React from 'react'
import { Formik } from 'formik'
import { Container, Header } from 'semantic-ui-react'
import { useSnackbar } from 'notistack'

import { mount, getAPIErrorMessage, getAPIFormErrors } from 'utils'
import { useCreateCaseMutation } from 'api'
import { CaseForm } from 'forms/case'

interface DjangoContext {
  topic_options: { key: string; value: string; text: string }[]
}
const CONTEXT = (window as any).REACT_CONTEXT as DjangoContext

const App = () => {
  const [createCase] = useCreateCaseMutation()
  const { enqueueSnackbar } = useSnackbar()
  return (
    <Container>
      <Header as="h1">Create a new case</Header>
      <Formik
        initialValues={{}}
        validate={(values) => { }}
        onSubmit={(values, { setSubmitting, setErrors }) => {
          createCase({ issueCreate: values })
            .unwrap()
            .then((caseResponse) => {
              window.location.href = caseResponse.url
            })
            .catch((err) => {
              enqueueSnackbar(
                getAPIErrorMessage(err, 'Failed to create a new case'),
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
        {(formik) => <CaseForm
          formik={formik}
          topicOptions={CONTEXT.topic_options}
          create
          editable />}
      </Formik>
    </Container>
  )
}
mount(App)
