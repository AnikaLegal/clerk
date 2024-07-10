import React, { useState, useMemo, useEffect } from 'react'
import api, { Task, TaskCreate } from 'api'
import {
  Container,
  Header,
  Grid,
  Segment,
  Rail,
  Form,
  Button,
  Dropdown,
  Card,
  Comment,
  Divider,
  Loader,
} from 'semantic-ui-react'
import {
  getAPIErrorMessage,
  getAPIFormErrors,
  mount,
  choiceToMap,
  choiceToOptions,
  markdownToHtml,
} from 'utils'
import {
  ModelType,
  Model,
  SetModel,
  UpdateModel,
  ModelChoices,
  UserPermission,
} from 'types'
import { getFormSchema, AutoForm, getModelInitialValues } from 'comps/auto-form'
import { FIELD_TYPES } from 'comps/field-component'
import { CaseSummaryCard } from 'comps/case-summary-card'
import { Formik } from 'formik'
import { useSnackbar } from 'notistack'
import * as Yup from 'yup'
import moment from 'moment'
import styled from 'styled-components'

const StyledCommentGroup = styled(Comment.Group)`
  && {
    max-width: 100%;
  }
`

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
            <TaskComments task={task} />
          </Segment>
        </CenteredDiv>
        <TaskRail
          task={task}
          setTask={setTask}
          update={update}
          choices={choices}
          perms={perms}
        />
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

interface TaskProps<Type extends ModelType> {
  task: Type
  setTask: SetModel<Type>
  update: UpdateModel<Type>
  choices: ModelChoices
  perms: UserPermission
}

export const TaskBody = ({
  task,
  setTask,
  update,
  choices,
  perms,
}: TaskProps<Task>) => {
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

export const TaskRail = ({
  task,
  setTask,
  update,
  choices,
  perms,
}: TaskProps<Task>) => {
  const [users, setUsers] = useState([])
  const [isUsersLoading, setIsUsersLoading] = useState(false)
  const [getUsers] = api.useLazyGetUsersQuery()

  const statusOptions = useMemo(() => choiceToOptions(choices.status), [])
  const { enqueueSnackbar } = useSnackbar()

  useEffect(() => {
    setIsUsersLoading(true)
    getUsers({ isActive: true, sort: 'email' })
      .unwrap()
      .then((users) => {
        setUsers(users)
        setIsUsersLoading(false)
      })
      .catch(() => setIsUsersLoading(false))
  }, [])

  const handleChange = (name: string, value: any) => {
    update({ [name]: value })
      .then((instance) => {
        enqueueSnackbar(`Updated task`, { variant: 'success' })
        setTask(instance)
      })
      .catch((err) => {
        enqueueSnackbar(getAPIErrorMessage(err, `Failed to update this task`), {
          variant: 'error',
        })
      })
  }

  return (
    <Rail attached position="right">
      <Card fluid>
        <Card.Content>
          <Grid>
            <Grid.Row columns={2}>
              <Grid.Column>
                <Header sub>Status</Header>
                <Dropdown
                  value={task.status}
                  options={statusOptions}
                  onChange={(e, { value }) => handleChange('status', value)}
                />
              </Grid.Column>
              <Grid.Column>
                <Header sub>Days Open</Header>
                {task.days_open}
              </Grid.Column>
            </Grid.Row>
            <Grid.Row columns={2}>
              <Grid.Column>
                <Header sub>Date Created</Header>
                {task.created_at}
              </Grid.Column>
              <Grid.Column>
                <Header sub>Date Closed</Header>
                {task.closed_at || '-'}
              </Grid.Column>
            </Grid.Row>
            <Grid.Row columns={1}>
              <Grid.Column>
                <Header sub>Assigned To</Header>
                <Dropdown
                  search
                  disabled={!perms.is_paralegal_or_better}
                  selectOnNavigation={false}
                  loading={isUsersLoading}
                  value={task.assigned_to.id}
                  options={users.map((u) => ({
                    key: u.id,
                    value: u.id,
                    text: u.email,
                  }))}
                  onChange={(e, { value }) =>
                    handleChange('assigned_to_id', value)
                  }
                />
              </Grid.Column>
            </Grid.Row>
            <Grid.Row columns={1}>
              <Grid.Column>
                <Header sub>Owner</Header>
                <Dropdown
                  search
                  disabled={!perms.is_coordinator_or_better}
                  selectOnNavigation={false}
                  loading={isUsersLoading}
                  value={task.owner.id}
                  options={users.map((u) => ({
                    key: u.id,
                    value: u.id,
                    text: u.email,
                  }))}
                  onChange={(e, { value }) => handleChange('owner_id', value)}
                />
              </Grid.Column>
            </Grid.Row>
          </Grid>
        </Card.Content>
      </Card>
      <CaseSummaryCard issue={task.issue} />
    </Rail>
  )
}

export const TaskComments = ({ task }: { task: Task }) => {
  const commentResults = api.useGetTaskCommentsQuery({ id: task.id })
  const comments = commentResults.data || []

  return (
    <StyledCommentGroup>
      <Divider />
      <Header as="h4">Comments</Header>
      <Loader inverted inline active={commentResults.isLoading} />
      {comments.map((comment) => (
        <Segment key={comment.id}>
          <Comment>
            <Comment.Content>
              <Comment.Author as="a">
                {comment.creator.full_name}
              </Comment.Author>
              <Comment.Metadata>
                <div>{moment(comment.created_at).fromNow()}</div>
              </Comment.Metadata>
              <Comment.Text>{comment.text}</Comment.Text>
            </Comment.Content>
          </Comment>
        </Segment>
      ))}
    </StyledCommentGroup>
  )
}

mount(App)
