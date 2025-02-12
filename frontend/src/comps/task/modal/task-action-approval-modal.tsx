import api, { TaskCreate } from 'api'
import { ModalProps } from 'comps/task/task-action-card'
import { enqueueSnackbar } from 'notistack'
import React from 'react'
import { Button, Form, Modal } from 'semantic-ui-react'
import { getAPIErrorMessage } from 'utils'
import { DropdownField, RichTextAreaField } from 'forms/formik'
import { Formik, FormikHelpers } from 'formik'
import * as Yup from 'yup'

const RequestApprovalSchema: Yup.ObjectSchema<TaskCreate> = Yup.object({
  assigned_to_id: Yup.number().required(),
  description: Yup.string().default(undefined).min(1).required(),
  issue_id: Yup.string().required(),
  name: Yup.string().required(),
  type: Yup.string().required(),
  /* Below not strictly necessary but prevents type error */
  due_at: Yup.string().notRequired(),
  is_approval_required: Yup.boolean().notRequired(),
  is_approved: Yup.boolean().notRequired(),
  is_urgent: Yup.boolean().notRequired(),
  status: Yup.string().notRequired(),
})

export const RequestApprovalModal = (props: ModalProps) => {
  const [createTask] = api.useCreateTaskMutation()

  const initialValues = {
    type: 'APPROVAL_REQUEST',
    name: `Approval request from ${props.user.full_name}`,
    issue_id: props.task.issue.id,
    assigned_to_id: props.task.issue.lawyer?.id,
    description: '',
  }

  const handleSubmit = (
    values: TaskCreate,
    helpers: FormikHelpers<TaskCreate>
  ) => {
    createTask({ taskCreate: values })
      .unwrap()
      .then(() =>
        enqueueSnackbar('Created approval request', { variant: 'success' })
      )
      .catch((e) =>
        enqueueSnackbar(
          getAPIErrorMessage(e, 'Failed to create approval request'),
          {
            variant: 'error',
          }
        )
      )
    helpers.resetForm()
    props.onClose()
  }

  return (
    <Formik
      enableReinitialize
      isInitialValid={false}
      initialValues={initialValues}
      onSubmit={handleSubmit}
      validationSchema={RequestApprovalSchema}
    >
      {(formik) => {
        const closeHandler = () => {
          formik.resetForm()
          props.onClose()
        }

        return (
          <Modal size="tiny" open={props.open} onClose={closeHandler}>
            <Modal.Header>Request approval for this task</Modal.Header>
            <Modal.Content>
              <Form
                onSubmit={formik.handleSubmit}
                error={Object.keys(formik.errors).length > 0}
              >
                <UserDropdownField {...props} />
                <RichTextAreaField
                  required
                  name="description"
                  label="Briefly explain what you are requesting approval for"
                />
              </Form>
            </Modal.Content>
            <Modal.Actions>
              <Button
                primary
                type="submit"
                onClick={() => formik.handleSubmit()}
                disabled={formik.isSubmitting || !formik.isValid}
              >
                Request approval
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
  const userResults = api.useGetUsersQuery({ isActive: true })
  const lawyer = props.task.issue.lawyer

  let users = userResults.data ? [...userResults.data] : []

  /* Exclude the current user.
  /* Exclude the supervising lawyer if they are present (we add back irrespective
   * below).
   * Include only lawyers.
   */
  users = users.filter(
    (user) =>
      user.id != props.user.id &&
      lawyer &&
      user.id != lawyer.id &&
      user.is_lawyer
  )
  /* Sort by full name.
   */
  users = users.sort((a, b) => a.full_name.localeCompare(b.full_name))

  /* Add the supervising lawyer as the first item.
   */
  if (lawyer && !userResults.isLoading) {
    users.unshift(lawyer)
  }

  const userOptions = users.map((u) => ({
    key: u.id,
    value: u.id,
    text: u.full_name || u.email,
    description: (lawyer && u.id === lawyer.id && 'Case Lawyer') || '',
  }))

  return (
    <DropdownField
      name="assigned_to_id"
      label="To"
      required
      search
      options={userOptions}
      loading={userResults.isLoading}
    />
  )
}
