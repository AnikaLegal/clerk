import api, { Task, TaskCommentCreate, TaskCreate } from 'api'
import { AutoForm, getFormSchema, getModelInitialValues } from 'comps/auto-form'
import { CaseSummaryCard } from 'comps/case-summary-card'
import { FIELD_TYPES } from 'comps/field-component'
import { TaskActionsCard, TaskCommentGroup, TaskMetaCard } from 'comps/task'
import { Formik } from 'formik'
import { enqueueSnackbar } from 'notistack'
import React, { useMemo, useState } from 'react'
import { Button, Divider, Form, Grid, Header, Segment } from 'semantic-ui-react'
import { Model, ModelChoices, UserPermission } from 'types'
import { TaskDetailProps, TaskStatus } from 'types/task'
import { choiceToMap, getAPIErrorMessage, getAPIFormErrors, mount } from 'utils'
import * as Yup from 'yup'

import {
  Editor,
  resetEditor,
  RichTextCommentEditor,
  RichTextDisplay,
} from 'comps/richtext-editor'

interface DjangoContext {
  choices: {
    status: [string, string][]
    type: [string, string][]
  }
  status: TaskStatus
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
      status={CONTEXT.status}
    />
  )
}

export const TaskDetail = ({
  data,
  choices,
  perms,
  status,
}: {
  data: Task
  choices: ModelChoices
  perms: UserPermission
  status: TaskStatus
}) => {
  const [task, setTask] = useState<Task>(data)
  const [updateTask] = api.useUpdateTaskMutation()

  const update = (values: Model) =>
    updateTask({
      id: task.id,
      taskCreate: values as TaskCreate,
    }).unwrap()

  return (
    <Grid columns="equal" relaxed>
      <Grid.Row>
        <Grid.Column>
          <CaseSummaryCard issue={task.issue} />
        </Grid.Column>
        <Grid.Column
          width={8}
          style={{ marginRight: '6rem', marginLeft: '6rem' }}
        >
          <Segment basic style={{ paddingTop: '0' }}>
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
            <TaskComments
              task={task}
              setTask={setTask}
              update={update}
              choices={choices}
              perms={perms}
            />
          </Segment>
        </Grid.Column>
        <Grid.Column>
          <TaskActionsCard
            task={task}
            setTask={setTask}
            update={update}
            perms={perms}
            status={status}
          />
          <TaskMetaCard
            task={task}
            setTask={setTask}
            update={update}
            choices={choices}
            perms={perms}
          />
        </Grid.Column>
      </Grid.Row>
    </Grid>
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
                <RichTextDisplay content={task.description} />
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
        enqueueSnackbar('Updated task', { variant: 'success' })
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
      type: FIELD_TYPES.RICHTEXT,
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

export const TaskComments = ({ task }: TaskDetailProps) => {
  const [createTaskComment] = api.useCreateTaskCommentMutation()

  const commentResult = api.useGetTaskCommentsQuery({ id: task.id })
  const comments = commentResult.data || []

  const handleSubmit = (editor: Editor) => {
    if (!editor.isEmpty && editor.getText().trim() != '') {
      const values: TaskCommentCreate = {
        text: editor.getHTML(),
      }
      createTaskComment({
        id: task.id,
        taskCommentCreate: values,
      })
        .then((instance) => {
          enqueueSnackbar('Added comment', { variant: 'success' })
          resetEditor(editor)
        })
        .catch((err) => {
          enqueueSnackbar(getAPIErrorMessage(err, 'Failed to add comment'), {
            variant: 'error',
          })
        })
    }
  }

  return (
    <>
      <RichTextCommentEditor
        onSubmit={handleSubmit}
        placeholder="Leave a comment…"
      />
      <TaskCommentGroup comments={comments} loading={commentResult.isLoading} />
    </>
  )
}

mount(App)
