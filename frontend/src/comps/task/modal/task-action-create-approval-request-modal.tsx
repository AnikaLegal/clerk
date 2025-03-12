import api, { TaskRequestCreate } from 'api'
import { DiscardChangesConfirmationModal } from 'comps/modal'
import { ModalProps } from 'comps/task/task-action-card'
import { Formik, FormikHelpers } from 'formik'
import { RichTextEditorField } from 'forms/formik'
import { enqueueSnackbar } from 'notistack'
import React, { useState } from 'react'
import { Button, Form, Icon, Message, Modal } from 'semantic-ui-react'
import { getAPIErrorMessage } from 'utils'
import * as Yup from 'yup'

const ApprovalRequestSchema: Yup.ObjectSchema<TaskRequestCreate> = Yup.object({
  type: Yup.string().oneOf(['APPROVAL']).required(),
  name: Yup.string().required(),
  comment: Yup.string().min(1).required(),
  to_user_id: Yup.number().required(),
})

export const RequestApprovalModal = ({
  task,
  setTask,
  user,
  open,
  onClose,
}: ModalProps) => {
  const [createTaskRequest] = api.useCreateTaskRequestMutation()
  const [getTask] = api.useLazyGetTaskQuery()
  const [confirmationOpen, setConfirmationOpen] = useState(false)

  const issue = task.issue
  const initialValues: TaskRequestCreate = {
    type: 'APPROVAL',
    name: `Approval request from ${user.full_name}`,
    comment: '',
    // @ts-expect-error
    // If the lawyer is not set we include a message and the user cannot submit
    // the request.
    to_user_id: issue.lawyer?.id,
  }

  const updateTask = () => {
    getTask({ id: task.id })
      .unwrap()
      .then((task) => {
        setTask(task)
      })
  }

  const handleSubmit = (
    values: TaskRequestCreate,
    { resetForm }: FormikHelpers<TaskRequestCreate>
  ) => {
    createTaskRequest({ id: task.id, taskRequestCreate: values })
      .unwrap()
      .then(() => {
        enqueueSnackbar('Created approval request', { variant: 'success' })
        updateTask()
        onClose()
        resetForm()
      })
      .catch((e) => {
        const mesg = getAPIErrorMessage(e, 'Failed to create approval request')
        enqueueSnackbar(mesg, { variant: 'error' })
      })
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
        const confirmDiscardHandler = () => {
          setConfirmationOpen(false)
          onClose()
          formik.resetForm()
        }
        const cancelDiscardHandler = () => {
          setConfirmationOpen(false)
        }
        const closeHandler = () => {
          if (formik.dirty) {
            setConfirmationOpen(true)
          } else {
            onClose()
            formik.resetForm()
          }
        }

        return (
          <>
            <DiscardChangesConfirmationModal
              open={confirmationOpen}
              onConfirm={confirmDiscardHandler}
              onCancel={cancelDiscardHandler}
            />
            <Modal size="small" open={open} onClose={closeHandler}>
              <Modal.Header>Request approval to close this task</Modal.Header>
              <Modal.Content>
                {!issue.lawyer && (
                  <Message negative>
                    <Icon name="warning" />
                    Cannot request approval as no case supervisor is assigned.
                  </Message>
                )}
                <p>
                  This task requires approval to close. Briefly explain what you
                  need approved including links to relevant documents or draft
                  emails:
                </p>
                <Form
                  onSubmit={formik.handleSubmit}
                  error={Object.keys(formik.errors).length > 0}
                >
                  <RichTextEditorField name="comment" />
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
          </>
        )
      }}
    </Formik>
  )
}
