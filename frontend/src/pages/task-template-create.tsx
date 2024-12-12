import { TaskTriggerCreate, useCreateTaskTriggerMutation } from 'api'
import { Formik, FormikHelpers } from 'formik'
import { TaskTemplateForm } from 'forms/task-template'
import { enqueueSnackbar } from 'notistack'
import React from 'react'
import { Container, Header } from 'semantic-ui-react'
import { getAPIFormErrors, mount } from 'utils'

interface DjangoContext {
  choices: {
    topic: string[][]
    event: string[][]
    event_stage: string[][]
    tasks_assignment_role: string[][]
    task_type: string[][]
  }
}

const CONTEXT = (window as any).REACT_CONTEXT as DjangoContext

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

  const initialValues = {
    name: '',
    topic: '',
    event: '',
    event_stage: '',
    tasks_assignment_role: '',
    templates: [],
  }

  return (
    <Container>
      <Header as="h1">Create a new task template</Header>
      <TaskTemplateForm
        initialValues={initialValues}
        onSubmit={handleSubmit}
        choices={CONTEXT.choices}
        create
      />
    </Container>
  )
}

mount(App)
