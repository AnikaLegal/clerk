import api, { TaskCreate } from 'api'
import { ModalProps } from 'comps/task/task-action-card'
import { Formik, FormikHelpers } from 'formik'
import { DropdownField } from 'forms/formik'
import { enqueueSnackbar } from 'notistack'
import React from 'react'
import { Button, Form, Modal } from 'semantic-ui-react'
import { getAPIErrorMessage } from 'utils'
import * as Yup from 'yup'

const QuestionSchema: Yup.ObjectSchema<TaskCreate> = Yup.object({
  assigned_to_id: Yup.number().required(),
  /* Below not strictly necessary but prevents type error */
  description: Yup.string().notRequired(),
  issue_id: Yup.string().notRequired(),
  name: Yup.string().notRequired(),
  type: Yup.string().notRequired(),
  due_at: Yup.string().notRequired(),
  is_approval_required: Yup.boolean().notRequired(),
  is_approved: Yup.boolean().notRequired(),
  is_urgent: Yup.boolean().notRequired(),
  status: Yup.string().notRequired(),
  related_task_id: Yup.number().notRequired(),
})

export const ReassignTaskModal = (props: ModalProps) => {
  const [createTask] = api.useCreateTaskMutation()

  const initialValues = {
    assigned_to_id: props.task.assigned_to?.id,
  }

  const handleSubmit = (
    values: TaskCreate,
    helpers: FormikHelpers<TaskCreate>
  ) => {
    props
      .update(values)
      .then((instance) => {
        enqueueSnackbar('Reassigned task', { variant: 'success' })
        props.setTask(instance)
      })
      .catch((e) => {
        enqueueSnackbar(getAPIErrorMessage(e, 'Failed to reassign task'), {
          variant: 'error',
        })
      })
    helpers.resetForm()
    props.onClose()
  }

  return (
    <Formik
      enableReinitialize
      isInitialValid={false}
      initialValues={initialValues}
      onSubmit={handleSubmit}
      validationSchema={QuestionSchema}
    >
      {(formik) => {
        const closeHandler = () => {
          formik.resetForm()
          props.onClose()
        }

        return (
          <Modal size="tiny" open={props.open} onClose={closeHandler}>
            <Modal.Header>Reassign the task</Modal.Header>
            <Modal.Content>
              <Form
                onSubmit={formik.handleSubmit}
                error={Object.keys(formik.errors).length > 0}
              >
                <UserDropdownField {...props} />
              </Form>
            </Modal.Content>
            <Modal.Actions>
              <Button
                primary
                type="submit"
                onClick={() => formik.handleSubmit()}
                disabled={!formik.isValid}
              >
                Reassign task
              </Button>
              <Button onClick={closeHandler}>Close</Button>
            </Modal.Actions>
          </Modal>
        )
      }}
    </Formik>
  )
}

const UserDropdownField = (props: ModalProps) => {
  const userResults = api.useGetUsersQuery({ isActive: true, sort: 'email' })
  let users = userResults.data ? [...userResults.data] : []

  /* Only include:
   * - The current assignee.
   * - The case paralegal.
   * - All coordinators plus.
   * You can't assign to another paralegal user as they cannot access the case
   * or task. You need to reassign the case to that paralegal and the associated
   * tasks will be reassigned automatically.
   */
  const assignee = props.task.assigned_to
  const paralegal = props.task.issue.paralegal
  users = users.filter((user) =>
    user.id == assignee?.id ||
    user.id == paralegal?.id ||
    props.task.is_approval_request
      ? user.is_lawyer
      : user.is_coordinator_or_better
  )

  const userOptions = users.map((u) => ({
    key: u.id,
    value: u.id,
    text: u.email,
  }))

  return (
    <DropdownField
      name="assigned_to_id"
      label="Reassign to"
      required
      search
      options={userOptions}
      loading={userResults.isLoading}
    />
  )
}
