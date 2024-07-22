import React from 'react'
import { Container, Header } from 'semantic-ui-react'
import { useSnackbar } from 'notistack'
import { mount, getAPIErrorMessage, getAPIFormErrors } from 'utils'
import { Formik } from 'formik'
import { useCreateTaskTriggerMutation } from 'api'
import { TaskTemplateForm } from 'forms/task-template'

interface DjangoContext {
  choices: {
    topic: string[][]
    event: string[][]
    event_stage: string[][]
    tasks_assignment_role: string[][]
  }
}

const CONTEXT = (window as any).REACT_CONTEXT as DjangoContext

const App = () => {
  const [createTaskTrigger] = useCreateTaskTriggerMutation()
  const { enqueueSnackbar } = useSnackbar()

  return (
    <Container>
      <Header as="h1">Create a new task template</Header>
      <Formik
        initialValues={{
          name: '',
          topic: '',
          event: '',
          event_stage: '',
          tasks_assignment_role: '',
          templates: [],
        }}
        validate={(values) => {}}
        onSubmit={(values, { setSubmitting, setErrors }) => {
          createTaskTrigger({ taskTriggerCreate: values })
            .unwrap()
            .then((template) => {
              window.location.href = template.url
            })
            .catch((e) => {
              enqueueSnackbar(
                getAPIErrorMessage(e, 'Failed to create a new task template'),
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
            create
          />
        )}
      </Formik>
    </Container>
  )
}

mount(App)
