import { Task, TaskRequestUpdate } from 'api'
import { DiscardChangesConfirmationModal } from 'comps/modal'
import { ModalProps } from 'comps/task/task-action-card'
import { Formik } from 'formik'
import { RichTextAreaField } from 'forms/formik'
import React, { useState } from 'react'
import { Button, Form, Modal } from 'semantic-ui-react'
import * as Yup from 'yup'

const ApprovalDecisionSchema: Yup.ObjectSchema<TaskRequestUpdate> = Yup.object({
  status: Yup.string().oneOf(['PENDING', 'DONE']).required(),
  is_approved: Yup.boolean().required(),
  to_comment: Yup.string().when('is_approved', {
    is: false,
    then: (schema) => schema.min(1).required(),
    otherwise: (schema) => schema.optional(),
  }),
})

export type ApprovalDecision = 'APPROVED' | 'DECLINED'

interface ApprovalDecisionModalProps extends ModalProps {
  decision: ApprovalDecision
  updateRequest: (values: TaskRequestUpdate) => Promise<Task | void>
}

export const ApprovalDecisionModal = ({
  open,
  onClose,
  decision,
  updateRequest,
}: ApprovalDecisionModalProps) => {
  const [confirmationOpen, setConfirmationOpen] = useState(false)

  const initialValues: TaskRequestUpdate = {
    status: 'DONE',
    is_approved: decision == 'APPROVED',
    to_comment: '',
  }

  const handleSubmit = (values: TaskRequestUpdate, { setSubmitting }) => {
    updateRequest(values)
      .then(() => {
        onClose()
      })
      .finally(() => setSubmitting(false))
  }

  return (
    <Formik
      enableReinitialize
      isInitialValid={decision == 'APPROVED'}
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
                {decision == 'APPROVED'
                  ? 'Approve the request'
                  : 'Decline the request'}
              </Modal.Header>
              <Modal.Content>
                {decision == 'APPROVED' ? (
                  <p>
                    You may leave an <strong>optional</strong> comment.
                  </p>
                ) : (
                  <p>
                    Describe the changes necessary for the task to be approved.
                  </p>
                )}
                <Form
                  onSubmit={formik.handleSubmit}
                  error={Object.keys(formik.errors).length > 0}
                >
                  <RichTextAreaField
                    name="to_comment"
                    required={decision == 'DECLINED'}
                  />
                </Form>
              </Modal.Content>
              <Modal.Actions>
                <Button
                  primary
                  type="submit"
                  negative={decision == 'DECLINED'}
                  onClick={() => formik.handleSubmit()}
                  disabled={formik.isSubmitting || !formik.isValid}
                >
                  {decision == 'APPROVED'
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
