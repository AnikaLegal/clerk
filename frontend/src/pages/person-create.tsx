import React from 'react'
import { Formik } from 'formik'
import { Container, Header } from 'semantic-ui-react'
import { useSnackbar } from 'notistack'

import { mount, getAPIErrorMessage, getAPIFormErrors } from 'utils'
import { useCreatePersonMutation } from 'apiNew'
import { PersonForm } from 'forms/person'

const App = () => {
  const [createPerson] = useCreatePersonMutation()
  const { enqueueSnackbar } = useSnackbar()
  return (
    <Container>
      <Header as="h1">Create a new person</Header>
      <Formik
        initialValues={{
          full_name: '',
          email: '',
          address: '',
          phone_number: '',
          support_contact_preferences: '',
        }}
        validate={(values) => {}}
        onSubmit={(values, { setSubmitting, setErrors }) => {
          createPerson({ personCreate: values })
            .unwrap()
            .then((person) => {
              window.location.href = person.url
            })
            .catch((err) => {
              enqueueSnackbar(
                getAPIErrorMessage(err, 'Failed to create a new person'),
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
        {(formik) => <PersonForm formik={formik} create editable />}
      </Formik>
    </Container>
  )
}
mount(App)
