import { FileButton } from '@mantine/core'
import { useClickOutside } from '@mantine/hooks'
import api, {
  Issue,
  Task,
  TaskAttachment,
  TaskCommentCreate,
  TaskCreate,
} from 'api'
import { DiscreteButton } from 'comps/button'
import { CASE_TABS, CaseHeader, CaseTabUrls } from 'comps/case-header'
import { CommentInput } from 'comps/comment'
import { ErrorMessage } from 'comps/error-message'
import { Editor, RichTextDisplay } from 'comps/rich-text'
import {
  CreateTaskSchema,
  getTaskApprovalColor,
  TaskActionCard,
  TaskActivityGroup,
  TaskApprovalActionCard,
  TaskApprovalTableCell,
  TaskAssignedToNode,
  TaskDueDateTableCell,
  TaskInformationCard,
} from 'comps/task'
import { CreateTaskModal } from 'comps/task/modal'
import { TASK_STATUSES, TASK_TYPES } from 'consts'
import { Formik } from 'formik'
import { TaskForm } from 'forms'
import { default as moment } from 'moment'
import { enqueueSnackbar } from 'notistack'
import React, { useRef, useState } from 'react'
import {
  Button,
  ButtonProps,
  Container,
  Divider,
  Form,
  Grid,
  Header,
  Icon,
  Label,
  List,
  Loader,
  Pagination,
  Popup,
  Segment,
  Table,
} from 'semantic-ui-react'
import { Model, UserInfo } from 'types/global'
import { TaskDetailProps } from 'types/task'
import { getAPIErrorMessage, getAPIFormErrors, mount } from 'utils'

interface DjangoContext {
  case_pk: string
  task_pk?: number
  urls: CaseTabUrls
  user: UserInfo
}
const CONTEXT = (window as any).REACT_CONTEXT as DjangoContext

const App = () => {
  const caseId = CONTEXT.case_pk
  const taskId = CONTEXT.task_pk
  const urls = CONTEXT.urls
  const user = CONTEXT.user

  const caseResult = api.useGetCaseQuery({ id: caseId })
  if (caseResult.isFetching || !caseResult.data) {
    return null
  }

  const issue = caseResult.data.issue
  return (
    <Container>
      <CaseHeader issue={issue} activeTab={CASE_TABS.TASKS} urls={urls} />
      {!taskId ? (
        <Segment basic>
          <CaseTaskList issue={issue} user={user} />
        </Segment>
      ) : (
        <Segment basic style={{ marginTop: '0' }}>
          <CaseTaskDetail taskId={taskId} urls={urls} user={user} />
        </Segment>
      )}
    </Container>
  )
}

export interface CaseTaskListProps {
  issue: Issue
  user: UserInfo
}

export const CaseTaskList = ({ issue, user }: CaseTaskListProps) => {
  const [open, setOpen] = useState(false)

  return (
    <>
      <CreateTaskModal
        issue={issue}
        open={open}
        onClose={() => setOpen(false)}
        user={user}
      />
      <Grid>
        <Grid.Row>
          <Grid.Column style={{ flexGrow: '1' }}>
            <Header as="h2">Case tasks</Header>
          </Grid.Column>
          {issue.is_open && user.is_coordinator_or_better && (
            <Grid.Column style={{ width: 'auto' }}>
              <Button primary onClick={() => setOpen(true)}>
                Add a task
              </Button>
            </Grid.Column>
          )}
        </Grid.Row>
      </Grid>
      <CaseTasksTable issue={issue} />
    </>
  )
}

export interface CaseTasksTableProps {
  issue: Issue
}

export const CaseTasksTable = ({ issue }: CaseTasksTableProps) => {
  const [page, setPage] = useState<number | undefined>(undefined)

  const result = api.useGetTasksQuery({
    page: page,
    pageSize: 100,
    issue: issue.id,
  })
  if (result.isFetching) {
    return <Loader active inline="centered" />
  }

  if (!result.data || result.data.results.length == 0) {
    return (
      <Segment textAlign="center" secondary>
        <p>No tasks exist for this case.</p>
      </Segment>
    )
  }

  return (
    <>
      <Table celled structured>
        <Table.Header>
          <Table.Row>
            <Table.HeaderCell>Name</Table.HeaderCell>
            <Table.HeaderCell>Type</Table.HeaderCell>
            <Table.HeaderCell>Assigned To</Table.HeaderCell>
            <Table.HeaderCell>Status</Table.HeaderCell>
            <Table.HeaderCell>Approval?</Table.HeaderCell>
            <Table.HeaderCell>Open?</Table.HeaderCell>
            <Table.HeaderCell>Created</Table.HeaderCell>
            <Table.HeaderCell>Due date</Table.HeaderCell>
          </Table.Row>
        </Table.Header>
        <Table.Body>
          {result.data.results.map((task) => (
            <Table.Row>
              <Table.Cell>
                <a href={task.url}>{task.name}</a>
              </Table.Cell>
              <Table.Cell>{TASK_TYPES[task.type]}</Table.Cell>
              <Table.Cell>
                <TaskAssignedToNode task={task} />
              </Table.Cell>
              <Table.Cell>{TASK_STATUSES[task.status]}</Table.Cell>
              <TaskApprovalTableCell task={task} />
              <Table.Cell textAlign="center">
                {task.is_open ? (
                  <Icon name="check" color="green" />
                ) : (
                  <Icon name="close" color="yellow" />
                )}
              </Table.Cell>
              <Table.Cell>
                {moment(task.created_at).format('DD/MM/YYYY')}
              </Table.Cell>
              <TaskDueDateTableCell task={task} />
            </Table.Row>
          ))}
        </Table.Body>
      </Table>
      {result.data.item_count > result.data.results.length && (
        <Pagination
          activePage={result.data.current}
          onPageChange={(e, { activePage }) => {
            setPage(activePage ? +activePage : undefined)
          }}
          totalPages={result.data.page_count}
          style={{ marginTop: '1em' }}
          ellipsisItem={{
            content: <Icon name="ellipsis horizontal" />,
            icon: true,
          }}
          firstItem={{
            content: <Icon name="angle double left" />,
            icon: true,
          }}
          lastItem={{
            content: <Icon name="angle double right" />,
            icon: true,
          }}
          prevItem={{ content: <Icon name="angle left" />, icon: true }}
          nextItem={{ content: <Icon name="angle right" />, icon: true }}
        />
      )}
    </>
  )
}

export interface CaseTaskDetailProps {
  taskId: number
  urls: CaseTabUrls
  user: UserInfo
}

export const CaseTaskDetail = ({ taskId, user, urls }: CaseTaskDetailProps) => {
  const result = api.useGetTaskQuery({ id: taskId })

  if (result.isLoading) {
    return <Loader active inline="centered" />
  }
  if (result.isError) {
    return (
      <Grid centered>
        <Segment basic>
          <ErrorMessage error={result.error} />
        </Segment>
      </Grid>
    )
  }
  if (!result.data) {
    return null
  }
  return (
    <>
      <div style={{ marginBottom: '1rem' }}>
        <a href={urls.tasks}>Back to case tasks</a>
      </div>
      <CaseTaskDisplay initialTask={result.data} user={user} />
    </>
  )
}

export interface CaseTaskDisplayProps {
  initialTask: Task
  user: UserInfo
}

export const CaseTaskDisplay = ({
  initialTask,
  user,
}: CaseTaskDisplayProps) => {
  const [task, setTask] = useState<Task>(initialTask)
  const [updateTask] = api.useUpdateTaskMutation()

  const update = (values: Model) =>
    updateTask({
      id: task.id,
      taskCreate: values as TaskCreate,
    }).unwrap()

  return (
    <Grid columns="equal" relaxed>
      <Grid.Row>
        <Grid.Column width={12}>
          <Segment
            basic
            style={{ marginBottom: '0', paddingTop: '0', paddingBottom: '0' }}
          >
            <TaskBody
              task={task}
              setTask={setTask}
              update={update}
              user={user}
            />
          </Segment>
          <Segment basic style={{ marginTop: '0' }}>
            <Divider />
            <Header as="h4">Activity</Header>
            <TaskActivity task={task} user={user} />
          </Segment>
        </Grid.Column>
        <Grid.Column>
          <TaskInformationCard task={task} />
          {task.type == 'APPROVAL' ? (
            <TaskApprovalActionCard
              task={task}
              setTask={setTask}
              update={update}
              user={user}
            />
          ) : (
            <TaskActionCard
              task={task}
              setTask={setTask}
              update={update}
              user={user}
            />
          )}
        </Grid.Column>
      </Grid.Row>
    </Grid>
  )
}

export const TaskBody = ({ task, setTask, update, user }: TaskDetailProps) => {
  const [isEditMode, setEditMode] = useState(false)
  const toggleEditMode = () => setEditMode(!isEditMode)

  if (!isEditMode) {
    return (
      <Grid>
        <Grid.Row>
          <Grid.Column style={{ flexGrow: '1' }}>
            <TaskHeader task={task} />
          </Grid.Column>
          {user.is_coordinator_or_better && (
            <Grid.Column style={{ width: 'auto' }}>
              <Button
                onClick={toggleEditMode}
                size="tiny"
                disabled={!task.is_open}
              >
                Edit task
              </Button>
            </Grid.Column>
          )}
        </Grid.Row>
        <Grid.Row>
          <Grid.Column>
            <Form>
              <Form.Field>
                <RichTextDisplay content={task.description_display} />
              </Form.Field>
            </Form>
          </Grid.Column>
        </Grid.Row>
        <TaskAttachments task={task} />
      </Grid>
    )
  }

  const submitHandler = (values: TaskCreate, { setSubmitting, setErrors }) => {
    if (!user.is_lawyer_or_better) {
      values = {
        ...values,
        is_approved: undefined,
        is_approval_required: undefined,
      }
    }
    update(values)
      .then((instance) => {
        enqueueSnackbar('Updated task', { variant: 'success' })
        setTask(instance)
        toggleEditMode()
      })
      .catch((err) => {
        enqueueSnackbar(getAPIErrorMessage(err, `Failed to update task`), {
          variant: 'error',
        })
        const requestErrors = getAPIFormErrors(err)
        if (requestErrors) {
          setErrors(requestErrors)
        }
      })
      .finally(setSubmitting(false))
  }

  const initialValues: TaskCreate = {
    issue_id: task.issue_id,
    type: task.type,
    name: task.name,
    description: task.description,
    assigned_to_id: task.assigned_to_id,
    is_urgent: task.is_urgent,
    due_at: task.due_at,
    is_approval_required: task.is_approval_required,
  }

  return (
    <Formik
      enableReinitialize
      isInitialValid={false}
      initialValues={initialValues}
      onSubmit={submitHandler}
      validationSchema={CreateTaskSchema}
    >
      {(formik) => {
        return (
          <Grid>
            <Grid.Row>
              <Grid.Column>
                <TaskForm
                  formik={formik}
                  user={user}
                  typeChoices={TASK_TYPES}
                />
              </Grid.Column>
            </Grid.Row>
            <Grid.Row>
              <Grid.Column>
                <Button
                  primary
                  disabled={formik.isSubmitting}
                  loading={formik.isSubmitting}
                  onClick={formik.submitForm}
                >
                  Update task
                </Button>
                <Button
                  disabled={formik.isSubmitting}
                  loading={formik.isSubmitting}
                  onClick={toggleEditMode}
                >
                  Cancel
                </Button>
              </Grid.Column>
            </Grid.Row>
          </Grid>
        )
      }}
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

export interface TaskHeaderProps {
  task: Task
}

export const TaskHeader = ({ task }: TaskHeaderProps) => {
  const isOverdue = getIsOverdue(task)

  return (
    <>
      <Header as="h1">
        {task.name}
        <Header.Subheader>{TASK_TYPES[task.type]}</Header.Subheader>
      </Header>
      <span>
        <TaskApprovalHeader task={task} />
        {task.is_open && task.is_urgent && <Label color="red">Urgent</Label>}
        {task.is_open && isOverdue && <Label color="red">Overdue</Label>}
      </span>
    </>
  )
}

export const TaskApprovalHeader = ({ task }: { task: Task }) => {
  if (task.is_approval_required) {
    const color = getTaskApprovalColor(task)
    return (
      <Label color={color}>
        {task.is_approved
          ? 'Approved'
          : task.is_approval_pending
            ? 'Approval pending'
            : 'Requires approval'}
      </Label>
    )
  }
  return null
}

export interface TaskActivityProps {
  task: Task
  user: UserInfo
}

export const TaskActivity = ({ task, user }: TaskActivityProps) => {
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
      })
        .unwrap()
        .then(() => {
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
      <TaskActivityGroup
        activities={activities}
        loading={activityResult.isLoading}
      />
    </>
  )
}

interface TaskAttachmentsProps {
  task: Task
}

export const TaskAttachments = ({ task }: TaskAttachmentsProps) => {
  const [showAttachments, setShowAttachments] = useState(true)
  const [deleteTaskAttachment] = api.useDeleteTaskAttachmentMutation()

  const result = api.useGetTaskAttachmentsQuery({ id: task.id })
  const data = result.data || []

  const handleDelete = (attachment: TaskAttachment) => {
    deleteTaskAttachment({
      id: task.id,
      attachmentId: attachment.id,
    })
      .unwrap()
      .then((payload) => {
        enqueueSnackbar('Removed attachment', { variant: 'success' })
      })
      .catch((error) => {
        enqueueSnackbar(
          getAPIErrorMessage(error, 'Failed to remove attachment'),
          {
            variant: 'error',
          }
        )
      })
  }

  return (
    <>
      <Grid.Row>
        <Grid.Column>
          <List floated="right" horizontal>
            <List.Item>
              <TaskAttachmentButton task={task} isLoading={result.isLoading} />
            </List.Item>
          </List>
        </Grid.Column>
      </Grid.Row>
      {data.length > 0 && (
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
            <TaskAttachmentGroup attachments={data} onDelete={handleDelete} />
          )}
        </>
      )}
    </>
  )
}

interface TaskAttachmentButtonProps {
  task: Task
  isLoading: boolean
}

export const TaskAttachmentButton = ({
  task,
  isLoading,
}: TaskAttachmentButtonProps) => {
  const [createTaskAttachment] = api.useCreateTaskAttachmentMutation()
  const [isUploading, setIsUploading] = useState(false)
  const resetRef = useRef<() => void>(null)

  const handleChange = (files: File[]) => {
    if (files.length > 0) {
      for (const file of files) {
        setIsUploading(true)
        // TODO: would be nice if this could be typed.
        const values = new FormData()
        values.set('file', file)
        values.set('comment_id', '')

        createTaskAttachment({
          id: task.id,
          taskAttachmentCreate: values as any,
        })
          .unwrap()
          .then((payload) => {
            enqueueSnackbar('Added attachment', { variant: 'success' })
          })
          .catch((error) => {
            enqueueSnackbar(
              getAPIErrorMessage(error, 'Failed to add attachment'),
              {
                variant: 'error',
              }
            )
          })
          .finally(() => {
            resetRef.current?.()
            setIsUploading(false)
          })
      }
    }
  }

  return (
    <FileButton
      resetRef={resetRef}
      onChange={handleChange}
      multiple
      disabled={isLoading || isUploading}
    >
      {(props) => {
        if (isLoading || isUploading) {
          return <Loader active inline size="mini" />
        }
        return (
          <Popup
            mouseEnterDelay={1000}
            trigger={<Icon link name="attach" onClick={props.onClick} />}
          >
            Attach files
          </Popup>
        )
      }}
    </FileButton>
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
    if (onDelete) {
      onDelete(attachment)
    }
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
