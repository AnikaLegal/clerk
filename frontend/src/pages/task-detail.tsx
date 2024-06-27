import React, { useState, useMemo } from "react"
import { Container, Header, Grid, Divider, Segment, Rail, Form, Button, Dropdown } from "semantic-ui-react"

import api, { Task, TaskCreate } from "api"
import { getAPIErrorMessage, getAPIFormErrors, mount, choiceToMap, choiceToOptions, markdownToHtml } from 'utils'

import { ModelId, ModelType, Model, SetModel, UpdateModel, ModelChoices } from "types"
import { getFormSchema, AutoForm, getModelInitialValues, } from 'comps/auto-form'
import { FIELD_TYPES } from "comps/field-component"

import { Formik } from 'formik'
import { useSnackbar } from 'notistack'
import * as Yup from "yup"

interface DjangoContext {
  choices: {
    status: [string, string][]
    type: [string, string][]
  }
  task_pk: string
  list_url: string
}
const CONTEXT = (window as any).REACT_CONTEXT as DjangoContext

const App = () => {
  const taskResult = api.useGetTaskQuery({ id: CONTEXT.task_pk })
  if (taskResult.isLoading)
    return null
  return (
    <TaskDetails data={taskResult.data} choices={CONTEXT.choices} />
  )
}

export const TaskDetails = ({ data, choices }: { data: Task, choices: ModelChoices }) => {
  const [task, setTask] = useState<Task>(data)
  const [updateTask] = api.useUpdateTaskMutation()

  const update = (id: ModelId, values: Model) =>
    updateTask({
      id: task.id,
      taskCreate: values as TaskCreate,
    }).unwrap()

  return (
    <Container>
      <Segment basic>
        <TaskBody task={task} setTask={setTask} update={update} choices={choices} />
        <TaskRail task={task} setTask={setTask} update={update} choices={choices} />
        <Divider />
        {/* 
          <TaskComments />
        */}
      </Segment>
    </Container>
  )
}

export const MarkdownDisplay = ({ value }: { value: string }) => {
  return (
    <div dangerouslySetInnerHTML={{ __html: value ? markdownToHtml(value) : '-' }} />
  )
}


interface TaskProps<Type extends ModelType> {
  task: Type,
  setTask: SetModel<Type>,
  update: UpdateModel<Type>,
  choices: ModelChoices
}

export const TaskBody = ({ task, setTask, update, choices }: TaskProps<Task>) => {
  const [isEditMode, setEditMode] = useState(false)
  const typeLabels = useMemo(() => choiceToMap(choices.type), [])

  const { enqueueSnackbar } = useSnackbar()
  const toggleEditMode = () => setEditMode(!isEditMode)

  if (!isEditMode) {
    return (
      <Grid>
        <Grid.Row>
          <Grid.Column style={{ flexGrow: "1" }}>
            <Header as="h1">
              {task.name}
              <Header.Subheader>
                {typeLabels.get(task.type)}
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
                <MarkdownDisplay value={task.description} />
              </Form.Field>
            </Form>
          </Grid.Column>
        </Grid.Row>
      </Grid>
    )
  }

  const submit = (values: Model, { setSubmitting, setErrors }: any) => {
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
  }

  const fields = [
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
  const schema = getFormSchema(fields)

  return (
    <Formik initialValues={getModelInitialValues(fields, task)}
      validationSchema={schema} onSubmit={submit} >
      {(formik) => (
        <AutoForm
          fields={fields}
          choices={choices}
          formik={formik}
          onCancel={toggleEditMode}
          submitText="Update"
        />
      )}
    </Formik>
  )
}

export const TaskRail = ({ task, setTask, update, choices }: TaskProps<Task>) => {
  const statusOptions = useMemo(() => choiceToOptions(choices.status), [])
  const { enqueueSnackbar } = useSnackbar()

  const handleChange = (name: string, value: string) => {
    update(task.id, { [name]: value })
      .then((instance) => {
        enqueueSnackbar(`Updated task`, { variant: 'success' })
        setTask(instance)
      })
      .catch((err) => {
        enqueueSnackbar(
          getAPIErrorMessage(err, `Failed to update this task`),
          {
            variant: 'error',
          }
        )
      })
  }

  return (
    <Rail attached dividing position="right">
      <Segment basic>
        <Grid>
          <Grid.Row columns={2}>
            <Grid.Column>
              <Header sub>Status</Header>
              <Dropdown
                value={task.status}
                options={statusOptions}
                onChange={(e, { value }) => handleChange("status", value)}
              />
            </Grid.Column>
            <Grid.Column>
              <Header sub>Days Open</Header>
              {task.days_open}
            </Grid.Column>
          </Grid.Row>
          <Grid.Row columns={1}>
            <Grid.Column>
              <Header sub>Fileref</Header>
              <a href={task.issue.url}>{task.issue.fileref}</a>
            </Grid.Column>
          </Grid.Row>
          <Grid.Row columns={2}>
            <Grid.Column>
              <Header sub>Date Created</Header>
              {task.created_at}
            </Grid.Column>
            <Grid.Column>
              <Header sub>Date Closed</Header>
              {task.closed_at || "-"}
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
  )
}

mount(App)