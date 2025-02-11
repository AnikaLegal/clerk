import { TaskCreate, useGetUsersQuery } from 'api'
import { FormikProps } from 'formik'
import React from 'react'
import { Form } from 'semantic-ui-react'
import { UserInfo } from 'types/global'
import { choiceToOptions } from 'utils'
import {
  BooleanField,
  DateInputField,
  DropdownField,
  DropdownFieldProps,
  InputField,
  RichTextEditorField,
} from './formik'

interface TaskFormProps {
  formik: FormikProps<TaskCreate>
  user: UserInfo
  choices: {
    type: string[][]
  }
}

export const TaskForm = ({ formik, user, choices }: TaskFormProps) => {
  return (
    <Form
      onSubmit={formik.handleSubmit}
      error={Object.keys(formik.errors).length > 0}
    >
      <InputField required name="name" label="Name" />
      <DropdownField
        required
        name="type"
        label="Type"
        options={choiceToOptions(choices.type)}
      />
      <UserDropdownField
        required
        search
        name="assigned_to_id"
        label="Assigned To"
        initialValues={formik.initialValues}
      />
      <DateInputField name="due_at" label="Due date" dateFormat="DD/MM/YYYY" />
      <BooleanField name="is_urgent" label="Urgent?" />
      {user.is_lawyer_or_better && (
        <BooleanField name="is_approval_required" label="Approval required?" />
      )}
      <RichTextEditorField name="description" label="Description" />
    </Form>
  )
}

interface UserDropdownFieldProps extends DropdownFieldProps {
  initialValues: TaskCreate
}

const UserDropdownField = ({
  initialValues,
  ...props
}: UserDropdownFieldProps) => {
  const userResults = useGetUsersQuery({ isActive: true, sort: 'email' })
  const users = userResults.data || []

  /* Only include:
   * - The current assignee.
   * - The case paralegal.
   * - All coordinators plus.
   * You can't assign to another paralegal user as they cannot access the case
   * or task. You need to reassign the case to that paralegal and the associated
   * tasks will be reassigned automatically.
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
   */

  const userOptions = users.map((u) => ({
    key: u.id,
    value: u.id,
    text: u.email,
  }))

  return (
    <DropdownField
      options={userOptions}
      loading={userResults.isLoading}
      {...props}
    />
  )
}
