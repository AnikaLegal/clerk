import React from 'react'
import { Formik } from 'formik'
import { Container, Header } from 'semantic-ui-react'
import { useSnackbar } from 'notistack'

import { mount, getAPIErrorMessage, getAPIFormErrors } from 'utils'
import { useCreateUserMutation } from 'apiNew'
import { AccountForm } from 'forms/account'

const App = () => {
  const [createUser] = useCreateUserMutation()
  const { enqueueSnackbar } = useSnackbar()
  return (
    <Container>
      <Header as="h1">Invite a paralegal</Header>
      <Formik
        initialValues={{
          first_name: '',
          last_name: '',
          email: '',
        }}
        validate={(values) => {}}
        onSubmit={(values, { setSubmitting, setErrors }) => {
          createUser({ userCreate: { ...values, username: values.email } })
            .unwrap()
            .then((account) => {
              window.location.href = account.url
            })
            .catch((err) => {
              enqueueSnackbar(
                getAPIErrorMessage(err, 'Failed to invite a paralegal'),
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
        {(formik) => <AccountForm formik={formik} />}
      </Formik>
    </Container>
  )
}
mount(App)
