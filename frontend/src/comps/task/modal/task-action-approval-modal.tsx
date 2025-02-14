import api, { Task, TaskCreate, TaskRequestCreate } from 'api'
import { ModalProps } from 'comps/task/task-action-card'
import { enqueueSnackbar } from 'notistack'
import React from 'react'
import { Button, Form, Modal } from 'semantic-ui-react'
import { getAPIErrorMessage } from 'utils'
import { DropdownField, RichTextAreaField } from 'forms/formik'
import { Formik, FormikHelpers } from 'formik'
import * as Yup from 'yup'
import { UserInfo } from 'types/global'

const ApprovalRequestSchema: Yup.ObjectSchema<TaskRequestCreate> = Yup.object({
  type: Yup.string().equals(['APPROVAL']).required(),
  name: Yup.string().required(),
  description: Yup.string().default(undefined).min(1).required(),
  assigned_to_id: Yup.number().required(),
})

export const RequestApprovalModal = ({
  task,
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
          <Modal size="tiny" open={open} onClose={closeHandler}>
            <Modal.Header>Request approval for this task</Modal.Header>
            <Modal.Content>
              <Form
                onSubmit={formik.handleSubmit}
                error={Object.keys(formik.errors).length > 0}
              >
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
