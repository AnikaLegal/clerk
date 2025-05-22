import { useCreateCaseMutation } from 'api'
import { Formik } from 'formik'
import { ClientSelectSearchField, DropdownField } from 'forms/formik'
import { useSnackbar } from 'notistack'
import React from 'react'
import { Button, Container, Form, Header } from 'semantic-ui-react'
import { getAPIErrorMessage, getAPIFormErrors, mount } from 'utils'

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
        initialValues={{
          topic: '',
          client_id: '',
        }}
        onSubmit={(values, { setSubmitting, setErrors }) => {
          createCase({ issue: values })
            .unwrap()
            .then((caseResponse) => {
              window.location.href = caseResponse.url
            })
            .catch((e) => {
              enqueueSnackbar(
                getAPIErrorMessage(e, 'Failed to create a new case'),
                {
                  variant: 'error',
                }
              )
              const requestErrors = getAPIFormErrors(e)
              if (requestErrors) {
                setErrors(requestErrors)
              }
              setSubmitting(false)
            })
        }}
      >
        {({ handleSubmit, errors, isSubmitting }) => (
          <Form onSubmit={handleSubmit} error={Object.keys(errors).length > 0}>
            <Header as="h3">Case</Header>
            <DropdownField
              name="topic"
              label="Topic"
              placeholder="Select case topic"
              options={CONTEXT.topic_options}
            />
            <ClientSelectSearchField name="client_id" label="Client" />
            <Button
              primary
              type="submit"
              disabled={isSubmitting}
              loading={isSubmitting}
            >
              Create case
            </Button>
          </Form>
        )}
      </Formik>
    </Container>
  )
}
mount(App)
