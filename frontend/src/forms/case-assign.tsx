import {
  Alert,
  Button,
  Group,
  Loader,
  Paper,
  Select,
  SelectProps,
  Stack,
  Text,
  Title,
} from '@mantine/core'
import { useForm } from '@mantine/form'
import {
  GetUsersApiArg,
  useGetUsersQuery,
  User,
  useUpdateCaseMutation,
} from 'api'
import { showNotification } from 'comps/notification'
import React, { useEffect, useState } from 'react'
import { CaseDetailFormProps } from 'types'
import { getAPIErrorMessage, getAPIFormErrors } from 'utils'

interface AssignFormValues {
  paralegal_id: string | null
  lawyer_id: string | null
}

export const AssignForm: React.FC<CaseDetailFormProps> = ({
  issue,
  onCancel,
}) => {
  const [updateCase] = useUpdateCaseMutation()
  const form = useForm<AssignFormValues>({
    mode: 'uncontrolled',
    initialValues: {
      paralegal_id: issue.paralegal ? String(issue.paralegal.id) : null,
      lawyer_id: issue.lawyer ? String(issue.lawyer.id) : null,
    },
    validate: {
      lawyer_id: (value, values) => {
        if (value == null && values.paralegal_id !== null) {
          return 'A lawyer must be selected if a paralegal is assigned'
        }
        return null
      },
    },
  })

  const handleSubmit = (
    values: AssignFormValues,
    event: React.FormEvent<HTMLFormElement> | undefined
  ) => {
    event?.stopPropagation()
    form.setSubmitting(true)
    updateCase({
      id: issue.id,
      issueUpdate: {
        paralegal_id: values.paralegal_id ? Number(values.paralegal_id) : null,
        lawyer_id: values.lawyer_id ? Number(values.lawyer_id) : null,
      },
    })
      .unwrap()
      .then(() => {
        showNotification({
          type: 'success',
          message: 'Assignment success',
        })
      })
      .catch((e) => {
        showNotification({
          type: 'error',
          title: 'Assignment failed',
          message: getAPIErrorMessage(e),
        })
        const requestErrors = getAPIFormErrors(e)
        if (requestErrors) {
          form.setErrors(requestErrors)
        }
      })
      .finally(() => {
        form.setSubmitting(false)
      })
  }

  return (
    <Paper withBorder shadow="sm" p="md">
      <Title order={3}>Assign a paralegal to this case</Title>
      <Text mt="md">Select the case paralegal and supervising lawyer.</Text>
      <form onSubmit={form.onSubmit(handleSubmit)}>
        <Stack mt="lg" gap="md">
          <UserSelect
            {...form.getInputProps('paralegal_id')}
            key={form.key('paralegal_id')}
            clearable
            searchable
            disabled={form.submitting}
            label="Paralegal"
            placeholder="Select a paralegal"
            params={{
              group: 'Paralegal',
              isActive: true,
              sort: 'email',
            }}
            size="md"
          />
          <UserSelect
            {...form.getInputProps('lawyer_id')}
            key={form.key('lawyer_id')}
            clearable
            searchable
            disabled={form.submitting}
            label="Lawyer"
            placeholder="Select a lawyer"
            params={{
              group: 'Lawyer',
              isActive: true,
              sort: 'email',
            }}
            size="md"
          />
          {Object.entries(form.errors)
            .filter(([k]) => k === 'non_field_errors')
            .map(([k, v]) => (
              <Alert color="red" key={k}>
                {v}
              </Alert>
            ))}
          <Group mt="sm">
            <Button
              loading={form.submitting}
              disabled={form.submitting}
              color="green"
              type="submit"
              size="md"
            >
              Update
            </Button>
            <Button
              variant="default"
              disabled={form.submitting}
              onClick={onCancel}
              size="md"
            >
              Close
            </Button>
          </Group>
        </Stack>
      </form>
    </Paper>
  )
}

interface UserSelectProps extends SelectProps {
  params: GetUsersApiArg
}

const UserSelect = ({ params, ...props }: UserSelectProps) => {
  const [data, setData] = useState<User[]>([])
  const [args, setArgs] = useState<GetUsersApiArg>({
    ...params,
    page: 1,
    pageSize: 100,
  })
  const result = useGetUsersQuery(args)

  useEffect(() => {
    if (result.data) {
      setData((prev) => [...prev, ...result.data!.results])
      // If there are more pages, fetch the next one
      if (result.data.next !== null) {
        setArgs((prev) => ({ ...prev, page: args.page! + 1 }))
      }
    }
  }, [result.data])

  const showLoading =
    result.isLoading || result.isFetching || result.data?.next !== null

  return (
    <Select
      {...props}
      data={data.map((u) => ({
        value: String(u.id),
        label: u.email,
      }))}
      rightSection={showLoading && <Loader size="sm" />}
    />
  )
}

export default AssignForm
