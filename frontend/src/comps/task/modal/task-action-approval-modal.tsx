import api, { TaskRequestCreate } from 'api'
import { ModalProps } from 'comps/task/task-action-card'
import { Formik, FormikHelpers } from 'formik'
import { RichTextEditorField } from 'forms/formik'
import { enqueueSnackbar } from 'notistack'
import React from 'react'
import { Button, Form, Modal } from 'semantic-ui-react'
import { getAPIErrorMessage } from 'utils'
import * as Yup from 'yup'

const ApprovalRequestSchema: Yup.ObjectSchema<TaskRequestCreate> = Yup.object({
  type: Yup.string().equals(['APPROVAL']).required(),
  name: Yup.string().required(),
  description: Yup.string().default(undefined).min(1).required(),
  assigned_to_id: Yup.number().required(),
})

export const RequestApprovalModal = ({
  task,
  setTask,
  user,
  open,
  onClose,
}: ModalProps) => {
  const [createTaskRequest] = api.useCreateTaskRequestMutation()

  const issue = task.issue
  const initialValues: TaskRequestCreate = {
    type: 'APPROVAL',
    name: `Approval request from ${user.full_name}`,
    description: '',
    assigned_to_id: issue.lawyer?.id,
  }

  const handleSubmit = (
    values: TaskRequestCreate,
    helpers: FormikHelpers<TaskRequestCreate>
  ) => {
    createTaskRequest({ id: task.id, taskRequestCreate: values })
      .unwrap()
      .then((task) => {
        setTask(task)
        enqueueSnackbar('Created approval request', { variant: 'success' })
      })
      .catch((e) =>
        enqueueSnackbar(
          getAPIErrorMessage(e, 'Failed to create approval request'),
          {
            variant: 'error',
          }
        )
      )
    helpers.resetForm()
    onClose()
  }

  return (
    <Formik
      enableReinitialize
      isInitialValid={false}
      initialValues={initialValues}
      onSubmit={handleSubmit}
      validationSchema={ApprovalRequestSchema}
    >
      {(formik) => {
        const closeHandler = () => {
          formik.resetForm()
          onClose()
        }

        return (
          <Modal size="small" open={open} onClose={closeHandler}>
            <Modal.Header>Request approval to close this task</Modal.Header>
            <Modal.Content>
              <p>
                This task requires approval to close. Briefly explain what you
                need approved including links to relevant documents or draft
                emails:
              </p>
              <Form
                onSubmit={formik.handleSubmit}
                error={Object.keys(formik.errors).length > 0}
              >
                <RichTextEditorField name="description" />
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
