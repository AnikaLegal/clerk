import React, { useState, useEffect } from "react"

import { Container, Header, Grid, Divider } from "semantic-ui-react"
import { Segment, Rail, Form, Button, Dropdown } from "semantic-ui-react"
import { useSnackbar } from 'notistack'
import * as Yup from "yup"

import { getFormSchema, FormField } from 'comps/auto-form'
import { FIELD_TYPES } from "comps/field-component"
import { mount, choiceToMap, choiceToOptions } from "utils"
import api, { Task, TaskCreate } from "api"
import { markdownToHtml } from 'utils'

import { Formik } from 'formik'
import { getAPIErrorMessage, getAPIFormErrors } from 'utils'
import {
  AutoForm,
  getModelInitialValues,
} from 'comps/auto-form'

import { ModelId, ModelType, Model, SetModel, ModelChoices } from "types"

interface DjangoContext {
  choices: {
    status: string[][]
    type: string[][]
  }
  task_pk: string
  list_url: string
}
const CONTEXT = (window as any).REACT_CONTEXT as DjangoContext
const TYPE_LABELS = choiceToMap(CONTEXT.choices.type)

const App = () => {
  const [isLoading, setIsLoading] = useState(true)
  const [task, setTask] = useState<Task>()
  const [getTask] = api.useLazyGetTaskQuery()
  const [updateTask] = api.useUpdateTaskMutation()

  useEffect(() => {
    setIsLoading(true)
    getTask({ id: CONTEXT.task_pk })
      .unwrap()
      .then((task) => {
        setTask(task)
        setIsLoading(false)
      })
      .catch(() => setIsLoading(false))
  }, [])
  if (isLoading) return null

  const update = (id: ModelId, values: Model) =>
    updateTask({
      id: task.id,
      taskCreate: values as TaskCreate,
    }).unwrap()

  const choices = (formFields: FormField[], model: Model) =>
    formFields.reduce<ModelChoices>((accumulator, field) => {
      const choices = CONTEXT.choices?.[field.name]
      if (choices) {
        return { ...accumulator, [field.name]: choices }
      } else {
        return accumulator
      }
    }, {})

  return (
    <Container>
      <Segment basic>
        <TaskBody task={task} setTask={setTask} update={update} choices={choices} />
        <Rail dividing position="right">
          <Segment basic>
            <Grid>
              <Grid.Row>
                <Grid.Column>
                  <Header sub>Status</Header>
                  <Dropdown
                    value={task.status}
                    options={choiceToOptions(CONTEXT.choices.status)}
                  />
                </Grid.Column>
              </Grid.Row>
              <Grid.Row columns={2}>
                <Grid.Column>
                  <Header sub>Fileref</Header>
                  <a href={task.issue.url}>{task.issue.fileref}</a>
                </Grid.Column>
                <Grid.Column>
                  <Header sub>Days Open</Header>
                  {task.days_open}
                </Grid.Column>
              </Grid.Row>
              <Grid.Row columns={2}>
                <Grid.Column>
                  <Header sub>Assigned To</Header>
                  <a href={task.assigned_to.url}>{task.assigned_to.full_name}</a>
                </Grid.Column>
                <Grid.Column>
                  <Header sub>Owner</Header>
                  <a href={task.owner.url}>{task.owner.full_name}</a>
                </Grid.Column>
              </Grid.Row>
            </Grid>
          </Segment>
        </Rail>
        <Divider />
      </Segment>
    </Container>
  )
}

interface TaskBodyProps<Type extends ModelType> {
  task: Type,
  setTask: SetModel<Type>,
  update: (id: ModelId, values: Model) => Promise<Type>
  choices: (formFields: FormField[], model: Type) => ModelChoices
}

export const TaskBody = ({ task, setTask, update, choices }: TaskBodyProps<Task>) => {
  const { enqueueSnackbar } = useSnackbar()
  const [isEditMode, setEditMode] = useState(false)
  const toggleEditMode = () => setEditMode(!isEditMode)

  if (!isEditMode) {
    return (
      <Grid>
        <Grid.Row>
          <Grid.Column style={{ flexGrow: "1" }}>
            <Header as="h1">
              {task.name}
              <Header.Subheader>
                {TYPE_LABELS.get(task.type)}
              </Header.Subheader>
            </Header>
          </Grid.Column>
          <Grid.Column style={{ width: "auto" }}>
            <Button onClick={toggleEditMode}>
              Edit
            </Button>
          </Grid.Column>
        </Grid.Row>
        <Grid.Row>
          <Grid.Column>
            <Form>
              <Form.Field>
                <div dangerouslySetInnerHTML={{ __html: task.description ? markdownToHtml(task.description) : '-' }} />
              </Form.Field>
            </Form>
          </Grid.Column>
        </Grid.Row>
      </Grid>
    )
  }

  return (
    <Formik
      initialValues={getModelInitialValues(FIELDS, task)}
      validationSchema={SCHEMA}
      onSubmit={(
        values: { [fieldName: string]: unknown },
        { setSubmitting, setErrors }: any
      ) => {
        update(task.id, values)
          .then((instance) => {
            enqueueSnackbar(`Updated task`, { variant: 'success' })
            setTask(instance)
            toggleEditMode()
            setSubmitting(false)
          })
          .catch((err) => {
            enqueueSnackbar(
              getAPIErrorMessage(err, `Failed to update this task`),
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
        <AutoForm
          fields={FIELDS}
          choices={choices(FIELDS, task)}
          formik={formik}
          onCancel={toggleEditMode}
          submitText="Update"
        />
      )}
    </Formik>
  )
}


const FIELDS = [
  {
    label: "Name",
    schema: Yup.string().required("Required"),
    type: FIELD_TYPES.TEXT,
    name: "name",
  },
  {
    label: "Type",
    schema: Yup.string().required("Required"),
    type: FIELD_TYPES.SINGLE_CHOICE,
    name: "type",
  },
  {
    label: "Description",
    type: FIELD_TYPES.TEXTAREA,
    name: "description",
  },
]
const SCHEMA = getFormSchema(FIELDS)

mount(App)
