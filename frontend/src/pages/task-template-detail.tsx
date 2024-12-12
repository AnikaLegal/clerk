import { modals } from '@mantine/modals'
import api, { TaskTriggerCreate } from 'api'
import { FormikHelpers } from 'formik'
import { TaskTemplateForm } from 'forms/task-template'
import { enqueueSnackbar } from 'notistack'
import React from 'react'
import { Container, Header } from 'semantic-ui-react'
import { getAPIErrorMessage, getAPIFormErrors, mount } from 'utils'

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
  const [updateTaskTrigger] = api.useUpdateTaskTriggerMutation()
  const [deleteTaskTrigger] = api.useDeleteTaskTriggerMutation()

  const taskTriggerResult = api.useGetTaskTriggerQuery({
    id: CONTEXT.task_trigger_pk,
  })
  if (taskTriggerResult.isLoading) {
    return null
  }

  const handleSubmit = (
    values: TaskTriggerCreate,
    helpers: FormikHelpers<TaskTriggerCreate>
  ) => {
    updateTaskTrigger({
      id: CONTEXT.task_trigger_pk,
      taskTriggerCreate: values,
    })
      .unwrap()
      .then(() => {
        enqueueSnackbar('Updated task template', {
          variant: 'success',
        })
      })
      .catch((e) => {
        enqueueSnackbar(
          getAPIErrorMessage(e, 'Failed to update task template'),
          { variant: 'error' }
        )
        const requestErrors = getAPIFormErrors(e)
        if (requestErrors) {
          helpers.setErrors(requestErrors)
        }
      })
      .finally(() => helpers.setSubmitting(false))
  }

  const handleDelete = (event) => {
    event.preventDefault()
    modals.openConfirmModal({
      title: 'Are you sure you want to delete this task template?',
      centered: true,
      labels: { confirm: 'Delete task template', cancel: 'Cancel' },
      confirmProps: { color: 'red' },
      onConfirm: () => {
        deleteTaskTrigger({ id: CONTEXT.task_trigger_pk })
          .unwrap()
          .then(() => {
            window.location.href = CONTEXT.list_url
          })
          .catch((e) => {
            enqueueSnackbar(
              getAPIErrorMessage(
                e,
                'Failed to delete this notification template'
              ),
              {
                variant: 'error',
              }
            )
          })
      },
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
      <TaskTemplateForm
        initialValues={taskTriggerResult.data}
        choices={CONTEXT.choices}
        onSubmit={handleSubmit}
        onDelete={handleDelete}
      />
    </Container>
  )
}

mount(App)
