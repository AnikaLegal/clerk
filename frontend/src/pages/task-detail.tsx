import { FileButton } from '@mantine/core'
import { useClickOutside } from '@mantine/hooks'
import api, { Task, TaskAttachment, TaskCommentCreate, TaskCreate } from 'api'
import { AutoForm, getFormSchema, getModelInitialValues } from 'comps/auto-form'
import { DiscreteButton } from 'comps/button'
import { CaseSummaryCard } from 'comps/case-summary-card'
import { CommentInput } from 'comps/comment'
import { FIELD_TYPES } from 'comps/field-component'
import { Editor, RichTextDisplay } from 'comps/rich-text'
import { TaskActionCard, TaskActivityGroup, TaskMetaCard } from 'comps/task'
import { Formik } from 'formik'
import moment from 'moment'
import { enqueueSnackbar } from 'notistack'
import React, { useEffect, useMemo, useState } from 'react'
import {
  Button,
  ButtonProps,
  Divider,
  Form,
  Grid,
  Header,
  Icon,
  Label,
  List,
  Popup,
  Segment,
} from 'semantic-ui-react'
import { Model, UserInfo } from 'types/global'
import { TaskDetailProps, TaskStatus } from 'types/task'
import { choiceToMap, getAPIErrorMessage, getAPIFormErrors, mount } from 'utils'
import * as Yup from 'yup'

interface DjangoContext {
  choices: {
    status: [string, string][]
    type: [string, string][]
  }
  status: TaskStatus
  task_pk: number
  list_url: string
  user: UserInfo
}
const CONTEXT = (window as any).REACT_CONTEXT as DjangoContext

export interface TaskBodyProps extends TaskDetailProps {
  status: TaskStatus
}
export interface TaskHeaderProps extends TaskDetailProps {
  status: TaskStatus
}

const App = () => {
  const [getTask] = api.useLazyGetTaskQuery()
  const [updateTask] = api.useUpdateTaskMutation()
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const [task, setTask] = useState<Task>()

  const loadTask = () => {
    setIsLoading(true)
    getTask({ id: CONTEXT.task_pk })
      .unwrap()
      .then((instance) => {
        setTask(instance)
      })
      .finally(() => {
        setIsLoading(false)
      })
  }
  useEffect(() => loadTask(), [])

  if (isLoading) {
    return null
  }
  const choices = CONTEXT.choices
  const user = CONTEXT.user
  const status = CONTEXT.status
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
          <Segment
            basic
            style={{ marginBottom: '0', paddingTop: '0', paddingBottom: '0' }}
          >
            <TaskBody
              task={task}
              setTask={setTask}
              update={update}
              choices={choices}
              user={user}
              status={status}
            />
          </Segment>
          <Segment basic style={{ marginTop: '0' }}>
            <Divider />
            <Header as="h4">Activity</Header>
            <TaskActivity
              task={task}
              setTask={setTask}
              update={update}
              choices={choices}
              user={user}
            />
          </Segment>
        </Grid.Column>
        <Grid.Column>
          <TaskMetaCard choices={choices} task={task} />
          <TaskActionCard
            task={task}
            setTask={setTask}
            update={update}
            user={user}
            status={status}
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
  user,
  status,
}: TaskBodyProps) => {
  const [isEditMode, setEditMode] = useState(false)
  const toggleEditMode = () => setEditMode(!isEditMode)

  if (!isEditMode) {
    return (
      <Grid>
        <Grid.Row>
          <Grid.Column style={{ flexGrow: '1' }}>
            <TaskHeader
              task={task}
              setTask={setTask}
              update={update}
              choices={choices}
              user={user}
              status={status}
            />
          </Grid.Column>
          {user.is_coordinator_or_better && (
            <Grid.Column style={{ width: 'auto' }}>
              <Button
                onClick={toggleEditMode}
                size="tiny"
                disabled={!task.is_open}
              >
                Edit
              </Button>
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
        <Grid.Row>
          <Grid.Column>
            <List floated="right" horizontal>
              <List.Item>
                <TaskAttachmentButton task={task} />
              </List.Item>
            </List>
          </Grid.Column>
        </Grid.Row>
        <TaskAttachments task={task} />
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
      label: 'Due date',
      type: FIELD_TYPES.DATE,
      name: 'due_at',
    },
    {
      label: 'Urgent?',
      type: FIELD_TYPES.BOOL,
      name: 'is_urgent',
    },
    {
      label: 'Description',
      type: FIELD_TYPES.RICHTEXT,
      name: 'description',
    },
  ]

  /* Only include the approvals fields in the UI if the user has the privileges
   * to change them. */
  if (user.is_lawyer) {
    fields.splice(
      -1,
      0,
      {
        label: 'Approval required?',
        type: FIELD_TYPES.BOOL,
        name: 'is_approval_required',
      },
      {
        label: 'Approved?',
        type: FIELD_TYPES.BOOL,
        name: 'is_approved',
      }
    )
  }

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

const getIsOverdue = (task: Task): boolean => {
  if (task.due_at) {
    const now = moment().startOf('day')
    const due_at = moment(task.due_at, 'DD/MM/YYYY')
    return now.isAfter(due_at)
  }
  return false
}

export const TaskHeader = ({
  task,
  setTask,
  update,
  choices,
  user,
  status,
}: TaskHeaderProps) => {
  const typeLabels = useMemo(() => choiceToMap(choices.type), [])
  const isOverdue = getIsOverdue(task)

  return (
    <>
      <Header as="h1">
        {task.name}
        <Header.Subheader>{typeLabels.get(task.type)}</Header.Subheader>
      </Header>
      <span>
        {task.is_approved ? (
          <Label color="green">Approved</Label>
        ) : (
          task.is_approval_required && (
            <Label color="blue">Requires approval</Label>
          )
        )}
        {task.is_open && task.is_urgent && <Label color="red">Urgent</Label>}
        {task.is_open && isOverdue && <Label color="red">Overdue</Label>}
      </span>
    </>
  )
}

export const TaskActivity = ({ task, user }: TaskDetailProps) => {
  const [createTaskComment] = api.useCreateTaskCommentMutation()

  /* TODO: handle errors.
  */
  const activityResult = api.useGetTaskActivityQuery({ id: task.id })
  const activities = activityResult.data || []

  const handleSubmit = (editor: Editor) => {
    if (!editor.isEmpty && editor.getText().trim() != '') {
      const values: TaskCommentCreate = {
        text: editor.getHTML(),
        creator_id: user.id,
      }
      createTaskComment({
        id: task.id,
        taskCommentCreate: values,
      }).unwrap()
        .then((instance) => {
          enqueueSnackbar('Added comment', { variant: 'success' })
          editor.commands.clearContent()
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
      <CommentInput onSubmit={handleSubmit} placeholder="Leave a comment…" />
      <TaskActivityGroup activities={activities} loading={activityResult.isLoading} />
    </>
  )
}

interface TaskAttachmentButtonProps {
  task: Task
}

export const TaskAttachmentButton = ({ task }: TaskAttachmentButtonProps) => {
  const [createTaskAttachment] = api.useCreateTaskAttachmentMutation()

  const handleChange = (files: File[]) => {
    if (files.length > 0) {
      for (const file of files) {
        // TODO: would be nice if this could be typed.
        const values = new FormData()
        values.set('file', file)
        values.set('comment_id', '')

        createTaskAttachment({
          id: task.id,
          taskAttachmentCreate: values as any,
        })
          .unwrap()
          .then((instance) => {
            enqueueSnackbar('Added attachment', { variant: 'success' })
          })
          .catch((err) => {
            enqueueSnackbar(
              getAPIErrorMessage(err, 'Failed to add attachment'),
              {
                variant: 'error',
              }
            )
          })
      }
    }
  }

  return (
    <FileButton onChange={handleChange} multiple>
      {(props) => (
        <Popup
          mouseEnterDelay={1000}
          trigger={<Icon link name="attach" onClick={props.onClick} />}
        >
          Attach files
        </Popup>
      )}
    </FileButton>
  )
}

interface TaskAttachmentsProps {
  task: Task
}

export const TaskAttachments = ({ task }: TaskAttachmentsProps) => {
  const [showAttachments, setShowAttachments] = useState(true)
  const [deleteTaskAttachment] = api.useDeleteTaskAttachmentMutation()

  const attachmentResult = api.useGetTaskAttachmentsQuery({ id: task.id })
  const attachments = attachmentResult.data || []

  if (attachments.length === 0) {
    return null
  }

  const handleDelete = (attachment: TaskAttachment) => {
    deleteTaskAttachment({
      id: task.id,
      attachmentId: attachment.id,
    })
      .unwrap()
      .then((instance) => {
        enqueueSnackbar('Removed attachment', { variant: 'success' })
      })
      .catch((err) => {
        enqueueSnackbar(
          getAPIErrorMessage(err, 'Failed to remove attachment'),
          {
            variant: 'error',
          }
        )
      })
  }

  return (
    <>
      <Grid.Row style={{ paddingTop: '0' }}>
        <Grid.Column>
          <TaskAttachmentToggleButton
            open={showAttachments}
            onClick={() => setShowAttachments(!showAttachments)}
          />
        </Grid.Column>
      </Grid.Row>
      {showAttachments && (
        <TaskAttachmentGroup
          attachments={attachments}
          onDelete={handleDelete}
        />
      )}
    </>
  )
}

interface TaskAttachmentToggleButtonProps {
  open: boolean
}

export const TaskAttachmentToggleButton = ({
  open,
  ...props
}: TaskAttachmentToggleButtonProps | ButtonProps) => {
  return (
    <DiscreteButton icon {...props}>
      <span>
        <Icon name={open ? 'caret down' : 'caret right'} />
        <span>Attachments</span>
      </span>
    </DiscreteButton>
  )
}

interface TaskAttachmentGroupProps {
  attachments: TaskAttachment[]
  onDelete?: (TaskAttachment) => void
}
export const TaskAttachmentGroup = ({
  attachments,
  onDelete,
}: TaskAttachmentGroupProps) => {
  return attachments.map((attachment) => {
    return (
      <Grid.Row
        key={attachment.id}
        style={{ paddingTop: '0', paddingBottom: '0.5rem' }}
      >
        <Grid.Column>
          <TaskAttachmentGroupItem
            attachment={attachment}
            onDelete={onDelete}
          />
        </Grid.Column>
      </Grid.Row>
    )
  })
}

interface TaskAttachmentGroupItemProps {
  attachment: TaskAttachment
  onDelete?: (TaskAttachment) => void
}
export const TaskAttachmentGroupItem = ({
  attachment,
  onDelete,
}: TaskAttachmentGroupItemProps) => {
  const [showConfirmDelete, setShowConfirmDelete] = useState(false)
  const ref = useClickOutside(() => setShowConfirmDelete(false))

  const handleDelete = (event) => {
    event.stopPropagation()
    onDelete(attachment)
  }

  return (
    <Segment
      style={{
        display: 'flex',
        justifyContent: 'space-between',
        gap: '1rem',
        padding: '0.5rem',
        borderRadius: 'var(--mantine-radius-default)',
      }}
    >
      <div style={{ flexGrow: '0' }}>
        <Icon name="attach" />
      </div>
      <a href={attachment.url} download style={{ flexGrow: '1' }}>
        {attachment.name.split('/').slice(-1)}
      </a>
      <div style={{ flexGrow: '0' }}>
        {showConfirmDelete ? (
          <div ref={ref}>
            <Button negative compact size="mini" onClick={handleDelete}>
              Confirm delete
            </Button>
          </div>
        ) : (
          <Icon
            link
            name="trash alternate outline"
            onClick={() => {
              setShowConfirmDelete(true)
            }}
          />
        )}
      </div>
    </Segment>
  )
}

mount(App)
