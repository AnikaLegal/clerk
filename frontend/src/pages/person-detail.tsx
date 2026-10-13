import React, { useEffect, useState } from 'react'
import { Formik } from 'formik'
import { Container, Header, Loader, Message } from 'semantic-ui-react'
import { useSnackbar } from 'notistack'

import { mount, getAPIErrorMessage, getAPIFormErrors } from 'utils'
import { PersonForm } from 'forms/person'
import { CaseListTable } from 'comps/case-table'
import {
  useDeletePersonMutation,
  useUpdatePersonMutation,
  useGetPersonQuery,
  useGetCasesQuery,
  Person,
} from 'api'

interface DjangoContext {
  personId: number
  is_editable: boolean
  list_url: string
}

const TABLE_FIELDS = [
  'fileref',
  'topic',
  'client',
  'paralegal',
  'stage',
  'outcome',
]

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const { personId, is_editable, list_url } = (window as any)
  .REACT_CONTEXT as DjangoContext

export const PersonInfo = ({ personId }: { personId: number }) => {
  const personQuery = useGetPersonQuery({ id: personId })
  const [person, setPerson] = useState<Person | null>(null)
  const { enqueueSnackbar } = useSnackbar()
  const [deletePerson] = useDeletePersonMutation()
  const [updatePerson] = useUpdatePersonMutation()

  useEffect(() => {
    setPerson(null)
  }, [personId])

  if (personQuery.isLoading) {
    return <Loader active inline="centered" />
  }

  if (personQuery.isError) {
    const isForbidden =
      personQuery.error &&
      'status' in personQuery.error &&
      personQuery.error.status === 403
    return (
      <Message negative>
        {isForbidden
          ? 'You do not have permission to access info about this person'
          : 'Could not load person'}
      </Message>
    )
  }

  const currentPerson = person ?? personQuery.data
  if (!currentPerson) {
    return null
  }

  const handleDelete = (e: React.MouseEvent) => {
    e.preventDefault()
    if (window.confirm('Are you sure you want to delete this person?')) {
      deletePerson({ id: currentPerson.id })
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
    <>
      <Header as="h1">
        {currentPerson.full_name}
        <Header.Subheader>
          <a href={list_url}>Back to parties</a>
        </Header.Subheader>
      </Header>
      <Formik
        enableReinitialize
        initialValues={{
          full_name: currentPerson.full_name,
          email: currentPerson.email,
          address: currentPerson.address,
          phone_number: currentPerson.phone_number,
          support_contact_preferences:
            currentPerson.support_contact_preferences?.value ?? '',
        }}
        validate={() => {}}
        onSubmit={(values, { setSubmitting, setErrors }) => {
          updatePerson({ id: currentPerson.id, personCreate: values })
            .unwrap()
            .then((updatedPerson) => {
              enqueueSnackbar('Updated person', { variant: 'success' })
              setPerson(updatedPerson)
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
      <PersonCaseList personId={currentPerson.id} />
    </>
  )
}

export const PersonCaseList = ({ personId }: { personId: number }) => {
  // Cases where this person is the support worker, tenancy agent or tenancy landlord.
  // A negative pageSize returns every case instead of the first 14.
  const cases = useGetCasesQuery({ person: personId, pageSize: -1 })

  if (cases.isLoading) {
    return (
      <Loader active inline="centered">
        Loading cases
      </Loader>
    )
  }

  if (cases.isError) {
    return <Message negative>Could not load cases</Message>
  }

  if (!cases.data) {
    return null
  }

  return <CaseListTable issues={cases.data.results} fields={TABLE_FIELDS} />
}

const App = () => {
  return (
    <Container>
      <PersonInfo personId={personId} />
    </Container>
  )
}

mount(App)
