import React from 'react'
import { Container, Header } from 'semantic-ui-react'
import { useSnackbar } from 'notistack'
import { Formik } from 'formik'
import api, { TaskTrigger } from 'api'
import { mount, getAPIErrorMessage, getAPIFormErrors } from 'utils'
import { TaskTemplateForm } from 'forms/task-template'

interface DjangoContext {
  choices: {
    topic: string[][]
    event: string[][]
    event_stage: string[][]
    tasks_assignment_role: string[][]
    task_type: string[][]
  }
  list_url: string
  task_trigger_pk: number
}
const CONTEXT = (window as any).REACT_CONTEXT as DjangoContext

const App = () => {
  const { enqueueSnackbar } = useSnackbar()
  const [updateTaskTrigger] = api.useUpdateTaskTriggerMutation()
  const [deleteTaskTrigger] = api.useDeleteTaskTriggerMutation()

  const taskTriggerResult = api.useGetTaskTriggerQuery({
    id: CONTEXT.task_trigger_pk,
  })
  if (taskTriggerResult.isLoading) {
    return null
  }

  const handleDelete = (e) => {
    e.preventDefault()

    const isDelete = confirm(
      'Are you sure you want to delete this notification template?'
    )
    if (!isDelete) return

    deleteTaskTrigger({ id: CONTEXT.task_trigger_pk })
      .unwrap()
      .then(() => {
        window.location.href = CONTEXT.list_url
      })
      .catch((err) => {
        enqueueSnackbar(
          getAPIErrorMessage(
            err,
            'Failed to delete this notification template'
          ),
          {
            variant: 'error',
          }
        )
      })
  }

  return (
    <Container>
      <Header as="h1">
        Edit task template
        <Header.Subheader>
          <a href={CONTEXT.list_url}>Back to task templates</a>
        </Header.Subheader>
      </Header>
      <Formik
        initialValues={taskTriggerResult.data || ({} as TaskTrigger)}
        onSubmit={(values, { setSubmitting, setErrors, resetForm }) => {
          let updateData = values
          if (!values.event) {
            updateData = { ...values, event_stage: '' }
          }
          updateTaskTrigger({
            id: CONTEXT.task_trigger_pk,
            taskTriggerCreate: updateData,
          })
            .unwrap()
            .then(() => {
              enqueueSnackbar('Updated task template', {
                variant: 'success',
              })
              setSubmitting(false)
            })
            .catch((e) => {
              enqueueSnackbar(
                getAPIErrorMessage(e, 'Failed to update task template'),
                { variant: 'error' }
              )
              const requestErrors = getAPIFormErrors(e)
              if (requestErrors) {
                setErrors(requestErrors)
              }
              setSubmitting(false)
            })
        }}
      >
        {(formik) => (
          <TaskTemplateForm
            formik={formik}
            choices={CONTEXT.choices}
            onDelete={handleDelete}
          />
        )}
      </Formik>
    </Container>
  )
}

mount(App)