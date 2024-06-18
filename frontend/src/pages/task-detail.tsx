import React from "react"
import { Formik } from "formik"
import { Container, Header } from "semantic-ui-react"
import { useSnackbar } from "notistack"

import { mount, getAPIErrorMessage, getAPIFormErrors } from "utils"
import { useGetTaskQuery, useDeleteTaskMutation, useUpdateTaskMutation, Task } from "api"
import { choiceToMap } from "utils"

interface DjangoContext {
  choices: {
    status: string[][]
    type: string[][]
  }
  task_pk: string
  list_url: string
}

const CONTEXT = (window as any).REACT_CONTEXT as DjangoContext
const STATUS_LABELS = choiceToMap(CONTEXT.choices.status)
const TYPE_LABELS = choiceToMap(CONTEXT.choices.type)

const App = () => {
  const [updateTask, updateTaskResult] = useUpdateTaskMutation()
  const [deleteTask] = useDeleteTaskMutation()
  const { enqueueSnackbar } = useSnackbar()

  const taskResult = useGetTaskQuery({ id: CONTEXT.task_pk })
  const isInitialLoad = taskResult.isLoading
  if (isInitialLoad) return null
  const task = taskResult.data

  const handleDelete = (e) => {
    e.preventDefault()
    if (window.confirm("Are you sure you want to delete this task?")) {
      deleteTask({ id: task.id })
        .then(() => {
          window.location.href = CONTEXT.list_url
        })
        .catch((err) => {
          enqueueSnackbar(getAPIErrorMessage(err, "Failed to delete task"), {
            variant: "error",
          })
        })
    }
  }
  return (
    <Container>
      <TaskHeader task={task} />
      <Formik
        initialValues={{
          name: task.name,
          description: task.description,
        }}
        validate={(values) => { }}
        onSubmit={(values, { setSubmitting, setErrors }) => {
          updateTask({ id: task.id, taskCreate: values })
            .unwrap()
            .then((task) => {
              enqueueSnackbar("Updated task", { variant: "success" })
              setSubmitting(false)
            })
            .catch((err) => {
              enqueueSnackbar(
                getAPIErrorMessage(err, "Failed to update task"), {
                variant: "error",
              })
              const requestErrors = getAPIFormErrors(err)
              if (requestErrors) {
                setErrors(requestErrors)
              }
              setSubmitting(false)
            })
        }}
      >
      </Formik>
    </Container>
  )
}

interface TaskHeaderProps {
  task: Task
}
export const TaskHeader: React.FC<TaskHeaderProps> = ({
  task,
}) => {
  return (
    <>
      <Header as="h1">
        {task.name} (<a href={task.issue.url}>{task.issue.fileref}</a>)
        <div className="sub header">
          <div>
            Created {task.created_at}{task.closed_at && (", Closed ") + task.closed_at}
          </div>
          <div>
            {task.assigned_to ? (
              <span>
                Assigned to&nbsp;
                <a href={task.assigned_to.url}>{task.assigned_to.full_name},</a>
                &nbsp;
              </span>
            ) : (
              "Not assigned, "
            )}
            {task.owner ? (
              <span>
                Owned by&nbsp;
                <a href={task.owner.url}>{task.owner.full_name}</a>&nbsp;
              </span>
            ) : (
              "not owned"
            )}
          </div>
        </div>
      </Header>
      <span id="case-status" hx-swap-oob="true">
        {task.is_open ? (
          <div className="ui blue label">Task open</div>
        ) : (
          <div className="ui green label">Task closed</div>
        )}

        <div className="ui grey label">
          Status
          {task.status ? (
            <div className="detail">{STATUS_LABELS.get(task.status)}</div>
          ) : (
            <div className="detail">-</div>
          )}
        </div>
      </span>
    </>
  )
}

mount(App)
