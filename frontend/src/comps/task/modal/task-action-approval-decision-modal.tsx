import { TaskApprovalUpdate, useUpdateTaskApprovalMutation } from 'api'
import { DiscardChangesConfirmationModal } from 'comps/modal'
import { ModalProps } from 'comps/task/task-action-card'
import { Formik, FormikHelpers } from 'formik'
import { RichTextAreaField } from 'forms/formik'
import { enqueueSnackbar } from 'notistack'
import React, { useState } from 'react'
import { Button, Form, Modal } from 'semantic-ui-react'
import { getAPIErrorMessage } from 'utils'
import * as Yup from 'yup'

const ApprovalDecisionSchema: Yup.ObjectSchema<TaskApprovalUpdate> = Yup.object(
  {
    status: Yup.string().required(),
    requesting_task: Yup.object({
      is_approved: Yup.boolean().required(),
      is_approval_pending: Yup.boolean().required(),
      comment: Yup.string().optional(),
    }).required(),
  }
)

export enum ApprovalDecision {
  APPROVED,
  DECLINED,
}

interface ApprovalDecisionModalProps extends ModalProps {
  decision: ApprovalDecision
}

export const ApprovalDecisionModal = ({
  task,
  setTask,
  open,
  onClose,
  status,
  decision,
}: ApprovalDecisionModalProps) => {
  const [updateTaskApproval] = useUpdateTaskApprovalMutation()
  const [confirmationOpen, setConfirmationOpen] = useState(false)

  const initialValues: TaskApprovalUpdate = {
    status: status.finished,
    requesting_task: {
      is_approved: decision == ApprovalDecision.APPROVED,
      is_approval_pending: false,
    },
  }

  const handleSubmit = (values: TaskApprovalUpdate, { setSubmitting }) => {
    updateTaskApproval({
      id: task.id,
      taskApprovalUpdate: values,
    })
      .unwrap()
      .then((task) => {
        setTask(task)
        enqueueSnackbar('Updated task approval', { variant: 'success' })
        onClose()
      })
      .catch((e) => {
        enqueueSnackbar(
          getAPIErrorMessage(e, 'Failed to update task approval'),
          {
            variant: 'error',
          }
        )
      })
      .finally(() => setSubmitting(false))
  }

  return (
    <Formik
      enableReinitialize
      initialValues={initialValues}
      onSubmit={handleSubmit}
      validationSchema={ApprovalDecisionSchema}
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
              <Modal.Header>
                {decision == ApprovalDecision.APPROVED
                  ? 'Approve the request'
                  : 'Decline the request'}
              </Modal.Header>
              <Modal.Content>
                <p>
                  You may leave an <strong>optional</strong> comment with your
                  approval decision:
                </p>
                <Form
                  onSubmit={formik.handleSubmit}
                  error={Object.keys(formik.errors).length > 0}
                >
                  <RichTextAreaField name="requesting_task.comment" />
                </Form>
              </Modal.Content>
              <Modal.Actions>
                <Button
                  primary
                  type="submit"
                  negative={decision == ApprovalDecision.DECLINED}
                  onClick={() => formik.handleSubmit()}
                  disabled={formik.isSubmitting || !formik.isValid}
                >
                  {decision == ApprovalDecision.APPROVED
                    ? 'Approve request'
                    : 'Decline request'}
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
