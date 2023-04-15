import React from 'react'
import { Formik } from 'formik'
import { Container, Header } from 'semantic-ui-react'

import { mount } from 'utils'
import { api } from 'api'
import { PersonForm } from 'forms/person'

const App = () => (
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
        api.person.create(values).then(({ resp, data, errors }) => {
          if (errors) {
            setErrors(errors)
          } else if (resp.ok) {
            window.location.href = data.url
          }
          setSubmitting(false)
        })
      }}
    >
      {(formik) => <PersonForm formik={formik} create editable />}
    </Formik>
  </Container>
)

mount(App)
