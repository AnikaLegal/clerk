import React, { useState, useMemo } from 'react'
import api, { Task, TaskCreate } from 'api'
import {
  Container,
  Header,
  Grid,
  Segment,
  Rail,
  Form,
  Button,
  Divider,
} from 'semantic-ui-react'
import {
  getAPIErrorMessage,
  getAPIFormErrors,
  mount,
  choiceToMap,
  markdownToHtml,
} from 'utils'
import { Model, ModelChoices, UserPermission, TaskDetailProps } from 'types'
import { TaskCommentGroup, TaskMetaCard } from 'comps/task'
import { getFormSchema, AutoForm, getModelInitialValues } from 'comps/auto-form'
import { FIELD_TYPES } from 'comps/field-component'
import { CaseSummaryCard } from 'comps/case-summary-card'
import { Formik } from 'formik'
import { useSnackbar } from 'notistack'
import * as Yup from 'yup'
import styled from 'styled-components'

const CenteredDiv = styled.div`
  max-width: 76%;
  margin-left: auto;
  margin-right: auto;
`

interface DjangoContext {
  choices: {
    status: [string, string][]
    type: [string, string][]
  }
  task_pk: number
  list_url: string
  user: UserPermission
}
const CONTEXT = (window as any).REACT_CONTEXT as DjangoContext

const App = () => {
  const taskResult = api.useGetTaskQuery({ id: CONTEXT.task_pk })
  if (taskResult.isLoading) return null
  return (
    <TaskDetail
      data={taskResult.data}
      choices={CONTEXT.choices}
      perms={CONTEXT.user}
    />
  )
}

export const TaskDetail = ({
  data,
  choices,
  perms,
}: {
  data: Task
  choices: ModelChoices
  perms: UserPermission
}) => {
  const [task, setTask] = useState<Task>(data)
  const [updateTask] = api.useUpdateTaskMutation()

  const update = (values: Model) =>
    updateTask({
      id: task.id,
      taskCreate: values as TaskCreate,
    }).unwrap()

  return (
    <Container>
      <Segment basic>
        <CenteredDiv>
          <Segment basic>
            <TaskBody
              task={task}
              setTask={setTask}
              update={update}
              choices={choices}
              perms={perms}
            />
          </Segment>
          <Segment basic>
            <Divider />
            <Header as="h4">Comments</Header>
            <TaskCommentGroup task={task} />
          </Segment>
        </CenteredDiv>
        <Rail attached position="right">
          <TaskMetaCard
            task={task}
            setTask={setTask}
            update={update}
            choices={choices}
            perms={perms}
          />
          <CaseSummaryCard issue={task.issue} />
        </Rail>
      </Segment>
    </Container>
  )
}

export const MarkdownDisplay = ({ value }: { value: string }) => {
  return (
    <div
      dangerouslySetInnerHTML={{ __html: value ? markdownToHtml(value) : '-' }}
    />
  )
}

export const TaskBody = ({
  task,
  setTask,
  update,
  choices,
  perms,
}: TaskDetailProps) => {
  const [isEditMode, setEditMode] = useState(false)
  const typeLabels = useMemo(() => choiceToMap(choices.type), [])

  const { enqueueSnackbar } = useSnackbar()
  const toggleEditMode = () => setEditMode(!isEditMode)

  if (!isEditMode) {
    return (
      <Grid>
        <Grid.Row>
          <Grid.Column style={{ flexGrow: '1' }}>
            <Header as="h1">
              {task.name}
              <Header.Subheader>{typeLabels.get(task.type)}</Header.Subheader>
            </Header>
          </Grid.Column>
          {perms.is_coordinator_or_better && (
            <Grid.Column style={{ width: 'auto' }}>
              <Button onClick={toggleEditMode}>Edit</Button>
            </Grid.Column>
          )}
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
    update(values)
      .then((instance) => {
        enqueueSnackbar(`Updated task`, { variant: 'success' })
        setTask(instance)
        toggleEditMode()
        setSubmitting(false)
      })
      .catch((err) => {
        enqueueSnackbar(getAPIErrorMessage(err, `Failed to update this task`), {
          variant: 'error',
        })
        const requestErrors = getAPIFormErrors(err)
        if (requestErrors) {
          setErrors(requestErrors)
        }
        setSubmitting(false)
      })
  }

  const fields = [
    {
      label: 'Name',
      schema: Yup.string().required('Required'),
      type: FIELD_TYPES.TEXT,
      name: 'name',
    },
    {
      label: 'Type',
      schema: Yup.string().required('Required'),
      type: FIELD_TYPES.SINGLE_CHOICE,
      name: 'type',
    },
    {
      label: 'Description',
      type: FIELD_TYPES.TEXTAREA,
      name: 'description',
    },
  ]
  const schema = getFormSchema(fields)

  return (
    <Formik
      initialValues={getModelInitialValues(fields, task)}
      validationSchema={schema}
      onSubmit={submit}
    >
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

mount(App)
