import api, { TaskCreate } from 'api'
import { ModalProps } from 'comps/task/task-action-card'
import { enqueueSnackbar } from 'notistack'
import React from 'react'
import { Button, Form, Modal } from 'semantic-ui-react'
import { getAPIErrorMessage } from 'utils'
import { DropdownField, RichTextAreaField } from 'forms/formik'
import { Formik, FormikHelpers } from 'formik'
import * as Yup from 'yup'

const QuestionSchema: Yup.ObjectSchema<TaskCreate> = Yup.object({
  assigned_to_id: Yup.number().required(),
  description: Yup.string().min(1).required(),
  issue_id: Yup.string().required(),
  name: Yup.string().required(),
  type: Yup.string().required(),
  /* Below not strictly necessary but prevents type error */
  due_at: Yup.string().optional(),
  is_approval_required: Yup.boolean().optional(),
  is_approved: Yup.boolean().optional(),
  is_urgent: Yup.boolean().optional(),
  status: Yup.string().optional(),
})

export const QuestionModal = (props: ModalProps) => {
  const [createTask] = api.useCreateTaskMutation()

  const initialValues = {
    type: 'QUESTION',
    name: `Question from ${props.user.full_name}`,
    issue_id: props.task.issue.id,
    assigned_to_id: props.task.issue.lawyer?.id,
    description: '',
  }

  const handleSubmit = (
    values: TaskCreate,
    helpers: FormikHelpers<TaskCreate>
  ) => {
    values.description =
      `${props.user.full_name} asked a question about ` +
      `<a href="${props.task.url}">this task<a>:` +
      `<blockquote>${values.description}</blockquote>`

    createTask({ taskCreate: values })
      .unwrap()
      .then(() => enqueueSnackbar('Created question', { variant: 'success' }))
      .catch((e) =>
        enqueueSnackbar(getAPIErrorMessage(e, 'Failed to create question'), {
          variant: 'error',
        })
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
      validationSchema={QuestionSchema}
    >
      {(formik) => {
        const closeHandler = () => {
          formik.resetForm()
          props.onClose()
        }

        return (
          <Modal size="tiny" open={props.open} onClose={closeHandler}>
            <Modal.Header>Ask a question about this task</Modal.Header>
            <Modal.Content>
              <Form
                onSubmit={formik.handleSubmit}
                error={Object.keys(formik.errors).length > 0}
              >
                <UserDropdownField {...props} />
                <RichTextAreaField
                  required
                  name="description"
                  label="Question"
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
                Send
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
   * Include only coordinators plus.
   */
  users = users.filter(
    (user) =>
      user.id != props.user.id &&
      lawyer &&
      user.id != lawyer.id &&
      (user.is_system_account || user.is_coordinator_or_better)
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
