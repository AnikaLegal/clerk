import React from 'react'
import { Formik } from 'formik'
import { Container, Header } from 'semantic-ui-react'
import { useSnackbar } from 'notistack'

import { mount, getAPIErrorMessage, getAPIFormErrors } from 'utils'
import { CaseListTable } from 'comps/case-table'
import { useGetTaskQuery, useDeleteTaskMutation, useUpdateTaskMutation, Task } from 'api'

interface DjangoContext {
  task_pk: string
}
const { task_pk } = (window as any).REACT_CONTEXT as DjangoContext

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

const App = () => {
  const taskResult = useGetTaskQuery({ id: task_pk })
  const [updateTask, updateTaskResult] = useUpdateTaskMutation()
  const [deleteTask] = useDeleteTaskMutation()
  const { enqueueSnackbar } = useSnackbar()

  const isInitialLoad = taskResult.isLoading
  if (isInitialLoad) return null
  const task = taskResult.data

  const handleDelete = (e) => {
    e.preventDefault()
    if (window.confirm('Are you sure you want to delete this task?')) {
      deleteTask({ id: task.id })
        .then(() => {
          window.location.href = list_url // TODO
        })
        .catch((err) => {
          enqueueSnackbar(getAPIErrorMessage(err, 'Failed to delete task'), {
            variant: 'error',
          })
        })
    }
  }
  return (
    <Container>
      <Header as="h1">
        {task.name}
      </Header>
      <Formik
        initialValues={{
          name: task.name,
          description: task.description,
        }}
        validate={(values) => { }}
        onSubmit={(values, { setSubmitting, setErrors }) => {
          updateTask({ id: task.id, taskCreate: values })
            .unwrap()
            .then((task) => {
              enqueueSnackbar('Updated task', { variant: 'success' })
              setSubmitting(false)
            })
            .catch((err) => {
              enqueueSnackbar(
                getAPIErrorMessage(err, 'Failed to update task'), {
                variant: 'error',
              })
              const requestErrors = getAPIFormErrors(err)
              if (requestErrors) {
                setErrors(requestErrors)
              }
              setSubmitting(false)
            })
        }}
      >
      </Formik>
      {/* <CaseListTable issues={issues} fields={TABLE_FIELDS} /> */}
    </Container>
  )
}

mount(App)
