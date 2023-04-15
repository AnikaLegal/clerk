import React from 'react'
import { Formik } from 'formik'
import { Container, Header } from 'semantic-ui-react'

import { mount } from 'utils'
import { api } from 'api'
import { PersonForm } from 'forms/person'
import { Person } from 'types'
import { CaseListTable } from 'comps/case-table'

interface DjangoContext {
  person: Person
  is_editable: boolean
  issues: any
  list_url: string
}

const TABLE_FIELDS = [
  'fileref',
  'topic',
  'client',
  'paralegal',
  'created_at',
  'stage',
  'provided_legal_services',
  'outcome',
]

const { person, is_editable, issues, list_url } = (window as any)
  .REACT_CONTEXT as DjangoContext

const App = () => {
  const handleDelete = (e) => {
    e.preventDefault()
    if (window.confirm('Are you sure you want to delete this person?')) {
      api.person.delete(person.id).then(() => {
        window.location.href = list_url
      })
    }
  }
  return (
    <Container>
      <Header as="h1">
        {person.full_name}
        <Header.Subheader>
          <a href={list_url}>Back to parties</a>
        </Header.Subheader>
      </Header>
      <Formik
        initialValues={{
          full_name: person.full_name,
          email: person.email,
          address: person.address,
          phone_number: person.phone_number,
          support_contact_preferences: person.support_contact_preferences.value,
        }}
        validate={(values) => {}}
        onSubmit={(values, { setSubmitting, setErrors }) => {
          api.person.update(person.id, values).then(({ errors }) => {
            if (errors) {
              setErrors(errors)
            }
            setSubmitting(false)
          })
        }}
      >
        {(formik) => (
          <PersonForm
            formik={formik}
            create={false}
            editable={is_editable}
            handleDelete={handleDelete}
          />
        )}
      </Formik>
      <CaseListTable issues={issues} fields={TABLE_FIELDS} />
    </Container>
  )
}

mount(App)
