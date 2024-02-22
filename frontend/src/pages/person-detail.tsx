import React from 'react'
import { Formik } from 'formik'
import { Container, Header } from 'semantic-ui-react'
import { useSnackbar } from 'notistack'

import { mount, getAPIErrorMessage, getAPIFormErrors } from 'utils'
import { PersonForm } from 'forms/person'
import { CaseListTable } from 'comps/case-table'
import { useDeletePersonMutation, useUpdatePersonMutation, Person } from 'api'

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

const {
  person: initialPerson,
  is_editable,
  issues,
  list_url,
} = (window as any).REACT_CONTEXT as DjangoContext

const App = () => {
  const [person, setPerson] = React.useState<Person>(initialPerson)
  const { enqueueSnackbar } = useSnackbar()
  const [deletePerson] = useDeletePersonMutation()
  const [updatePerson] = useUpdatePersonMutation()
  const handleDelete = (e) => {
    e.preventDefault()
    if (window.confirm('Are you sure you want to delete this person?')) {
      deletePerson({ id: person.id })
        .then(() => {
          window.location.href = list_url
        })
        .catch((err) => {
          enqueueSnackbar(getAPIErrorMessage(err, 'Failed to delete person'), {
            variant: 'error',
          })
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
          updatePerson({ id: person.id, personCreate: values })
            .unwrap()
            .then((person) => {
              enqueueSnackbar('Updated person', { variant: 'success' })
              setPerson(person)
              setSubmitting(false)
            })
            .catch((err) => {
              enqueueSnackbar(
                getAPIErrorMessage(err, 'Failed to update this person'),
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
