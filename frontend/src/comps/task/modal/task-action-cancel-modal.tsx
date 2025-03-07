import api, { TaskStatus, TaskStatusUpdate } from 'api'
import { ModalProps } from 'comps/task/task-action-card'
import { Formik, FormikHelpers } from 'formik'
import { RichTextAreaField } from 'forms/formik'
import { enqueueSnackbar } from 'notistack'
import React from 'react'
import { Button, Form, Modal } from 'semantic-ui-react'
import { getAPIErrorMessage, getAPIFormErrors } from 'utils'
import * as Yup from 'yup'

export const CancelTaskModal = (props: ModalProps) => {
  const [updateTaskStatus] = api.useUpdateTaskStatusMutation()

  const schema: Yup.ObjectSchema<TaskStatusUpdate> = Yup.object({
    status: Yup.string().oneOf(["NOT_DONE"]).required(),
    comment: Yup.string().min(1).required(),
  })

  const initialValues: TaskStatusUpdate = {
    status: 'NOT_DONE',
  }

  const handleSubmit = (
    values: TaskStatusUpdate,
    helpers: FormikHelpers<TaskStatusUpdate>
  ) => {
    updateTaskStatus({ id: props.task.id, taskStatusUpdate: values })
      .unwrap()
      .then((task) => {
        props.setTask(task)
        enqueueSnackbar('Updated task status', { variant: 'success' })
        helpers.resetForm()
        props.onClose()
      })
      .catch((e) => {
        enqueueSnackbar(getAPIErrorMessage(e, 'Failed to update task status'), {
          variant: 'error',
        })
        const errors = getAPIFormErrors(e)
        if (errors) {
          helpers.setErrors(errors)
        }
      })
      .finally(() => helpers.setSubmitting(false))
  }

  return (
    <Formik
      enableReinitialize
      isInitialValid={false}
      initialValues={initialValues}
      onSubmit={handleSubmit}
      validationSchema={schema}
    >
      {(formik) => {
        const closeHandler = () => {
          formik.resetForm()
          props.onClose()
        }

        return (
          <Modal size="tiny" open={props.open} onClose={closeHandler}>
            <Modal.Header>Cancel the task</Modal.Header>
            <Modal.Content>
              <Form
                onSubmit={formik.handleSubmit}
                error={Object.keys(formik.errors).length > 0}
              >
                <RichTextAreaField
                  autoFocus
                  required
                  name="comment"
                  label="Briefly explain why the task was not completed"
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
                Cancel task
              </Button>
              <Button onClick={closeHandler}>Close</Button>
            </Modal.Actions>
          </Modal>
        )
      }}
    </Formik>
  )
}
