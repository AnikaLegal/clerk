import { TaskTriggerCreate, useCreateTaskTriggerMutation } from 'api'
import { Formik } from 'formik'
import { TaskTemplateForm } from 'forms/task-template'
import { useSnackbar } from 'notistack'
import React from 'react'
import { Container, Header } from 'semantic-ui-react'
import { getAPIFormErrors, mount } from 'utils'
import * as Yup from 'yup'

Yup.setLocale({ mixed: { required: 'This field is required.' } })
export const TaskTriggerSchema: Yup.ObjectSchema<TaskTriggerCreate> = Yup.object({
  name: Yup.string().required(),
  topic: Yup.string().required(),
  event: Yup.string().required(),
  tasks_assignment_role: Yup.string().required(),
  templates: Yup.array(),
  event_stage: Yup.string().when('event', {
    is: 'STAGE',
    then: (schema) => schema.required(),
  }),
})

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
        validationSchema={TaskTriggerSchema}
        onSubmit={(values, { setSubmitting, setErrors }) => {
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
                setErrors(requestErrors)
              }
              setSubmitting(false)
            })
        }}
      >
        {(formik) => (
          <TaskTemplateForm formik={formik} choices={CONTEXT.choices} create />
        )}
      </Formik>
    </Container>
  )
}

mount(App)
