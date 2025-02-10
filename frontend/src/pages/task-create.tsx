import {
  TaskCreate,
  useCreateTaskMutation,
  useGetCaseQuery,
  useGetUsersQuery,
} from 'api'
import { CaseSummaryCard } from 'comps/case-summary-card'
import { TaskForm } from 'forms'
import { enqueueSnackbar } from 'notistack'
import React from 'react'
import { Grid, Header } from 'semantic-ui-react'
import { Model, UserInfo } from 'types/global'
import { getAPIErrorMessage, getAPIFormErrors, mount } from 'utils'

interface DjangoContext {
  case_pk: string
  choices: {
    status: [string, string][]
    type: [string, string][]
  }
  user: UserInfo
  list_url: string
}
const CONTEXT = (window as any).REACT_CONTEXT as DjangoContext

const App = () => {
  const [createTask] = useCreateTaskMutation()
  const caseResult = useGetCaseQuery({ id: CONTEXT.case_pk })
  const userResults = useGetUsersQuery({ isActive: true, sort: 'email' })

  const issue = caseResult.data?.issue
  const users = userResults.data || []

  /* Only include:
   * - The current assignee.
   * - The case paralegal.
   * - All coordinators plus.
   * You can't assign to another paralegal user as they cannot access the case
   * or task. You need to reassign the case to that paralegal and the associated
   * tasks will be reassigned automatically.
   */
  const userOptions = users
    .filter(
      (u) =>
        u.id == issue?.paralegal?.id ||
        u.is_system_account ||
        u.is_coordinator_or_better
    )
    .map((u) => [u.id, u.email])

  const case_pk = CONTEXT.case_pk
  const choices = CONTEXT.choices
  const user = CONTEXT.user

  const submitHandler = (values: Model, { setSubmitting, setErrors }: any) => {
    createTask({
      taskCreate: values as TaskCreate,
    })
      .unwrap()
      .then((task) => {
        enqueueSnackbar('Created task', {
          variant: 'success',
          onExited: () => {
            window.location.href = task.url
          },
        })
      })
      .catch((err) => {
        enqueueSnackbar(getAPIErrorMessage(err, `Failed to create task`), {
          variant: 'error',
        })
        const requestErrors = getAPIFormErrors(err)
        if (requestErrors) {
          setErrors(requestErrors)
        }
      })
      .finally(() => setSubmitting(false))
  }

  const cancelHandler = () => {
    window.location.href = CONTEXT.list_url
  }

  return (
    <Grid columns="equal" relaxed>
      <Grid.Row>
        <Grid.Column>
          {!caseResult.isLoading && (
            <CaseSummaryCard issue={caseResult.data.issue} />
          )}
        </Grid.Column>
        <Grid.Column
          width={8}
          style={{ marginRight: '6rem', marginLeft: '6rem' }}
        >
          <Grid>
            <Grid.Row>
              <Grid.Column>
                <Header as="h1">Create a new task</Header>
              </Grid.Column>
            </Grid.Row>
            <Grid.Row>
              <Grid.Column>
                <TaskForm
                  initialValues={{
                    name: '',
                    description: '',
                    assigned_to_id: null,
                    type: '',
                    status: '',
                    issue_id: case_pk,
                    is_urgent: false,
                    is_approval_required: false,
                  }}
                  user={user}
                  choices={{ ...choices, assigned_to_id: userOptions }}
                  onSubmit={submitHandler}
                  onCancel={cancelHandler}
                  submitButtonText="Create"
                />
              </Grid.Column>
            </Grid.Row>
          </Grid>
        </Grid.Column>
        <Grid.Column>{/* Empty */}</Grid.Column>
      </Grid.Row>
    </Grid>
  )
}

mount(App)
