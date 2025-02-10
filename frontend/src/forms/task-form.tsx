import { Task, useGetUsersQuery } from 'api'
import { AutoForm, getFormSchema, getModelInitialValues } from 'comps/auto-form'
import { FIELD_TYPES } from 'comps/field-component'
import { Formik } from 'formik'
import React from 'react'
import { UserInfo } from 'types/global'
import * as Yup from 'yup'

interface TaskFormProps {
  task: Task
  user: UserInfo
  choices: any
  onSubmit: any
  onCancel?: null | (() => void)
  submitButtonText?: string
  cancelButtonText?: string
}

export const TaskForm = ({
  task,
  user,
  choices,
  onSubmit,
  onCancel,
  submitButtonText,
  cancelButtonText,
}: TaskFormProps) => {
  const userResults = useGetUsersQuery({ isActive: true, sort: 'email' })
  let users = userResults.data || []

  /* Only include:
   * - The current assignee.
   * - The case paralegal.
   * - All coordinators plus.
   * You can't assign to another paralegal user as they cannot access the case
   * or task. You need to reassign the case to that paralegal and the associated
   * tasks will be reassigned automatically.
   */
  const userOptions = users
    .filter(
      (u) =>
        u.id == task.assigned_to?.id ||
        u.id == task.issue.paralegal?.id ||
        (task.is_approval_request
          ? u.is_lawyer_or_better
          : u.is_system_account || u.is_coordinator_or_better)
    )
    .map((u) => [u.id, u.email])

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
  const initialValues = getModelInitialValues(fields, task)

  return (
    <Formik
      initialValues={initialValues}
      validationSchema={schema}
      onSubmit={onSubmit}
    >
      {(formik) => (
        <AutoForm
          fields={fields}
          choices={{ ...choices, assigned_to_id: userOptions }}
          formik={formik}
          onCancel={onCancel}
          submitText={submitButtonText}
          cancelText={cancelButtonText}
        />
      )}
    </Formik>
  )
}
