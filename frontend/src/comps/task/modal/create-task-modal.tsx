import api, { Issue, TaskCreate, TaskStatus, TaskType } from 'api'
import { DiscardChangesConfirmationModal } from 'comps/modal'
import { Formik, FormikHelpers } from 'formik'
import { TaskForm } from 'forms'
import { enqueueSnackbar } from 'notistack'
import React, { useState } from 'react'
import { Button, Modal } from 'semantic-ui-react'
import { UserInfo } from 'types/global'
import { getAPIErrorMessage, getAPIFormErrors } from 'utils'
import * as Yup from 'yup'

Yup.setLocale({ mixed: { required: 'This field is required.' } })

export const CreateTaskSchema: Yup.ObjectSchema<TaskCreate> = Yup.object({
  assigned_to_id: Yup.number().required(),
  issue_id: Yup.string().required(),
  name: Yup.string().required(),
  type: Yup.string<TaskType>().required(),
  description: Yup.string().optional(),
  due_at: Yup.string().optional(),
  is_approval_required: Yup.boolean().optional(),
  is_approved: Yup.boolean().optional(),
  is_urgent: Yup.boolean().optional(),
  status: Yup.string<TaskStatus>().optional(),
})

interface CreateTaskModalProps {
  issue: Issue
  onClose: () => void
  open: boolean
  user: UserInfo
  choices: {
    type: string[][]
  }
}

export const CreateTaskModal = ({
  issue,
  onClose,
  open,
  user,
  choices,
}: CreateTaskModalProps) => {
  const [createTask] = api.useCreateTaskMutation()
  const [confirmationOpen, setConfirmationOpen] = useState(false)

  const initialValues: TaskCreate = {
    issue_id: issue.id,
    name: '',
    // @ts-expect-error
    type: '',
    due_at: '',
    assigned_to_id: null,
    is_urgent: false,
    is_approval_required: false,
    description: '',
  }

  const handleSubmit = (
    values: TaskCreate,
    { setSubmitting, setErrors, resetForm }: FormikHelpers<TaskCreate>
  ) => {
    if (!user.is_lawyer_or_better) {
      values = {
        ...values,
        is_approved: undefined,
        is_approval_required: undefined,
      }
    }
    createTask({ taskCreate: values })
      .unwrap()
      .then(() => {
        enqueueSnackbar('Created task', { variant: 'success' })
        resetForm()
        onClose()
      })
      .catch((e) => {
        enqueueSnackbar(getAPIErrorMessage(e, 'Failed to create task'), {
          variant: 'error',
        })
        const requestErrors = getAPIFormErrors(e)
        if (requestErrors) {
          setErrors(requestErrors)
        }
      })
      .finally(() => setSubmitting(false))
  }

  return (
    <Formik
      enableReinitialize
      isInitialValid={false}
      initialValues={initialValues}
      onSubmit={handleSubmit}
      validationSchema={CreateTaskSchema}
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
            <Modal open={open} onClose={closeHandler}>
              <Modal.Header>Add a task</Modal.Header>
              <Modal.Content>
                <TaskForm formik={formik} choices={choices} user={user} />
              </Modal.Content>
              <Modal.Actions>
                <Button
                  primary
                  onClick={formik.submitForm}
                  disabled={formik.isSubmitting || !formik.isValid}
                  loading={formik.isSubmitting}
                >
                  Add task
                </Button>
                <Button
                  disabled={formik.isSubmitting}
                  onClick={closeHandler}
                  loading={formik.isSubmitting}
                >
                  Close
                </Button>
              </Modal.Actions>
            </Modal>
          </>
        )
      }}
    </Formik>
  )
}
