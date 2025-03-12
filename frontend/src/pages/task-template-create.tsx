import { TaskTriggerCreate, useCreateTaskTriggerMutation } from 'api'
import { FormikHelpers } from 'formik'
import { TaskTemplateForm } from 'forms/task-template'
import { enqueueSnackbar } from 'notistack'
import React from 'react'
import { Container, Header } from 'semantic-ui-react'
import { getAPIFormErrors, mount } from 'utils'

const App = () => {
  const [createTaskTrigger] = useCreateTaskTriggerMutation()

  const handleSubmit = (
    values: TaskTriggerCreate,
    helpers: FormikHelpers<TaskTriggerCreate>
  ) => {
    createTaskTrigger({ taskTriggerCreate: values })
      .unwrap()
      .then((template) => {
        window.location.href = template.url
      })
      .catch((e) => {
        enqueueSnackbar('Failed to create a new task template', {
          variant: 'error',
        })
        const requestErrors = getAPIFormErrors(e)
        if (requestErrors) {
          helpers.setErrors(requestErrors)
        }
        helpers.setSubmitting(false)
      })
  }

  const initialValues: TaskTriggerCreate = {
    name: '',
    // @ts-expect-error
    topic: '',
    // @ts-expect-error
    event: '',
    // @ts-expect-error
    event_stage: '',
    // @ts-expect-error
    tasks_assignment_role: '',
    templates: [],
  }

  return (
    <Container>
      <Header as="h1">Create a new task template</Header>
      <TaskTemplateForm
        initialValues={initialValues}
        onSubmit={handleSubmit}
        create
      />
    </Container>
  )
}

mount(App)
