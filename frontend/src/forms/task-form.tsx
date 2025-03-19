import { TaskCreate, useGetCaseQuery, useGetUsersQuery, User } from 'api'
import { FormikProps } from 'formik'
import moment from 'moment'
import React from 'react'
import { Form } from 'semantic-ui-react'
import { UserInfo } from 'types/global'
import { TaskTypes, TaskTypesWithoutRequestTypes } from 'types/task'
import {
  BooleanField,
  DateInputField,
  DropdownField,
  InputField,
  RichTextEditorField,
} from './formik'

interface TaskFormProps {
  formik: FormikProps<TaskCreate>
  user: UserInfo
  typeChoices: TaskTypes | TaskTypesWithoutRequestTypes
}

export const TaskForm = ({ formik, user, typeChoices }: TaskFormProps) => {
  const { users, isLoading } = getAssignedToUsers(formik.values)

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
        options={Object.entries(typeChoices).map(([key, value]) => ({
          key: key,
          value: key,
          text: value,
        }))}
      />
      <DropdownField
        required
        search
        name="assigned_to_id"
        label="Assigned To"
        options={users.map((u) => ({
          key: u.id,
          value: u.id,
          text: u.email,
        }))}
        loading={isLoading}
      />
      <DateInputField
        name="due_at"
        label="Due date"
        dateFormat="DD/MM/YYYY"
        minDate={moment().add(1, 'day')}
      />
      <BooleanField name="is_urgent" label="Urgent?" />
      {user.is_lawyer_or_better && (
        <BooleanField name="is_approval_required" label="Approval required?" />
      )}
      <RichTextEditorField name="description" label="Description" />
    </Form>
  )
}

const getAssignedToUsers = (
  values: TaskCreate
): { users: User[]; isLoading: boolean } => {
  const issueResult = useGetCaseQuery({ id: values.issue_id })
  const userResult = useGetUsersQuery({ isActive: true, sort: 'email' })

  if (issueResult.isLoading || userResult.isLoading) {
    return { users: [], isLoading: true }
  }
  const issue = issueResult.data?.issue
  const users = userResult.data
  if (!issue || !users) {
    return { users: [], isLoading: false }
  }

  /* Only include:
   *
   * - The current assignee, if any.
   * - The case paralegal.
   * - All coordinators plus.
   * - Special so-called system accounts.
   *
   * You can't assign to another paralegal user as they cannot access the case
   * or task. You need to reassign the case to that paralegal and the associated
   * tasks will be reassigned automatically.
   */
  return {
    users: users.filter(
      (u) =>
        u.id == values.assigned_to_id ||
        u.id == issue.paralegal?.id ||
        u.id == issue.lawyer?.id ||
        u.is_coordinator_or_better ||
        u.is_system_account
    ),
    isLoading: false,
  }
}
