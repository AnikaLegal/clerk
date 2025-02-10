import { TaskCreate } from 'api'
import { AutoForm, getFormSchema, getModelInitialValues } from 'comps/auto-form'
import { FIELD_TYPES } from 'comps/field-component'
import { Formik } from 'formik'
import React from 'react'
import { UserInfo } from 'types/global'
import * as Yup from 'yup'

interface TaskFormProps {
  user: UserInfo
  initialValues: TaskCreate
  choices: any
  onSubmit: any
  onCancel?: null | (() => void)
  submitButtonText?: string
  cancelButtonText?: string
}

export const TaskForm = ({
  user,
  initialValues,
  choices,
  onSubmit,
  onCancel,
  submitButtonText,
  cancelButtonText,
}: TaskFormProps) => {
  const fields = [
    {
      label: 'Name',
      schema: Yup.string().required('Required'),
      type: FIELD_TYPES.TEXT,
      name: 'name',
    },
    {
      label: 'Type',
      schema: Yup.string().required('Required'),
      type: FIELD_TYPES.SINGLE_CHOICE,
      name: 'type',
    },
    {
      label: 'Assigned To',
      schema: Yup.string().required('Required'),
      type: FIELD_TYPES.SINGLE_CHOICE,
      name: 'assigned_to_id',
    },
    {
      label: 'Due date',
      type: FIELD_TYPES.DATE,
      name: 'due_at',
    },
    {
      label: 'Urgent?',
      type: FIELD_TYPES.BOOL,
      name: 'is_urgent',
    },
    /* Only include in the UI if the user has the privileges to change. */
    ...(user.is_lawyer_or_better
      ? [
          {
            label: 'Approval required?',
            type: FIELD_TYPES.BOOL,
            name: 'is_approval_required',
          },
        ]
      : []),
    {
      label: 'Description',
      type: FIELD_TYPES.RICHTEXT,
      name: 'description',
    },
  ]
  const schema = getFormSchema(fields)

  return (
    <Formik
      initialValues={initialValues}
      validationSchema={schema}
      onSubmit={onSubmit}
    >
      {(formik) => (
        <AutoForm
          fields={fields}
          choices={choices}
          formik={formik}
          onCancel={onCancel}
          submitText={submitButtonText}
          cancelText={cancelButtonText}
        />
      )}
    </Formik>
  )
}
