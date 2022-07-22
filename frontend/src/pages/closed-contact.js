import React, { useState } from 'react'
import {
  Button,
  Container,
  Header,
  Table,
  Input,
  Dropdown,
} from 'semantic-ui-react'
import { Formik } from 'formik'
import * as Yup from 'yup'

import { mount } from 'utils'
import { api } from 'api'

import {
  AutoForm,
  getModelChoices,
  getModelInitialValues,
  getFormSchema,
  FIELD_TYPES,
} from 'comps/auto-form'

const FIELDS = [
  {
    label: 'Name',
    schema: Yup.string().required('Required'),
    type: FIELD_TYPES.TEXT,
    name: 'name',
  },
  {
    label: 'Email',
    type: FIELD_TYPES.EMAIL,
    name: 'email',
    schema: Yup.string().email().required('Required'),
  },
  {
    label: 'Rental problem',
    type: FIELD_TYPES.SINGLE_CHOICE,
    name: 'topic',
    schema: Yup.string().required('Required'),
  },
]
const SCHEMA = getFormSchema(FIELDS)
const MODEL = {
  topic: {
    choices: [
      ['REPAIRS', 'Repairs'],
      ['BONDS', 'Bonds'],
    ],
  },
}

const App = () => {
  const [isSuccess, setIsSuccess] = useState(false)
  return (
    <Container>
      <h1>Anika Legal is not currently taking new cases.</h1>
      <p>
        Due to high demand for our services, we have had to limit our support to
        existing clients. We're sorry for the inconvenience. If you'd like us to
        contact you when we are taking new cases, please fill the form below and
        provide your email address.
      </p>
      {isSuccess && (
        <p>
          We have received your contact request and will email you with a
          follow-up when we have capacity.
        </p>
      )}
      {!isSuccess && (
        <Formik
          initialValues={{
            name: '',
            email: '',
            topic: '',
          }}
          validationSchema={SCHEMA}
          onSubmit={(values, { setSubmitting, setErrors }) => {
            api.contact.create(values).then(({ resp, data }) => {
              if (resp.status === 400) {
                setErrors(data)
                setSubmitting(false)
              } else if (resp.ok) {
                setSubmitting(false)
                setIsSuccess(true)
              }
            })
          }}
        >
          {(formik) => (
            <AutoForm
              fields={FIELDS}
              choices={getModelChoices(FIELDS, MODEL)}
              formik={formik}
            />
          )}
        </Formik>
      )}
    </Container>
  )
}

mount(App)
