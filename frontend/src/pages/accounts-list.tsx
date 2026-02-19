import {
  Anchor,
  Button,
  Center,
  Container,
  Grid,
  Group,
  Loader,
  Pagination,
  Table,
  Text,
  Title,
} from '@mantine/core'
import { IconCheck, IconExclamationCircle, IconX } from '@tabler/icons-react'
import { GetUsersApiArg, useGetUsersQuery, User } from 'api'
import { SelectFilter, TextInputFilter } from 'comps/filter'
import { GroupLabels } from 'comps/group-label'
import { showNotification } from 'comps/notification'
import React, { useEffect, useState } from 'react'
import { UserPermission } from 'types'
import { getAPIErrorMessage, mount } from 'utils'

interface DjangoContext {
  user: UserPermission
  create_url: string
  group_values: string[]
}
const CONTEXT = (window as any).REACT_CONTEXT as DjangoContext

const App = () => {
  const [args, setArgs] = useState<GetUsersApiArg>({
    page: 1,
    sort: '-date_joined',
    isActive: true,
  })
  const result = useGetUsersQuery(args)

  const handleFilterChange = (key, value) => {
    setArgs((prevArgs) => ({
      ...prevArgs,
      [key]: value !== null ? value : undefined,
      page: 1, // Reset to first page on filter change
    }))
  }

  return (
    <Container size="xl">
      <Title order={1}>
        <Group wrap="nowrap" gap="sm" justify="space-between">
          <span>Accounts</span>
          {CONTEXT.user.is_admin_or_better && (
            <Button component="a" href={CONTEXT.create_url}>
              Invite users
            </Button>
          )}
        </Group>
      </Title>
      {!result.isLoading && result.data && (
        <Text c="dimmed">
          Showing {result.data.results.length} of {result.data.item_count}{' '}
          accounts
        </Text>
      )}
      <Grid mt="lg">
        <Grid.Col span={12}>
          <TextInputFilter
            name="name"
            label="Search"
            placeholder="Search by name"
            onFilterChange={handleFilterChange}
          />
        </Grid.Col>
        <Grid.Col span={6}>
          <SelectFilter
            name="group"
            data={CONTEXT.group_values.map((group) => ({
              value: group,
              label: group,
            }))}
            label="Group"
            value={args.group || ''}
            onFilterChange={handleFilterChange}
          />
        </Grid.Col>
        <Grid.Col span={6}>
          <SelectFilter
            name="isActive"
            data={[
              { value: 'true', label: 'Yes' },
              { value: 'false', label: 'No' },
            ]}
            label="Active?"
            value={args.isActive?.toString() || ''}
            onFilterChange={handleFilterChange}
          />
        </Grid.Col>
      </Grid>
      <Table
        withColumnBorders
        withTableBorder
        verticalSpacing="xs"
        fz="md"
        mt="lg"
      >
        <Table.Thead>
          <Table.Tr>
            <Table.Th>Name</Table.Th>
            <Table.Th>Org</Table.Th>
            <Table.Th>Email</Table.Th>
            <Table.Th>Created</Table.Th>
            <Table.Th>Groups</Table.Th>
            <Table.Th>Active?</Table.Th>
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>
          <TableBody result={result} dataRow={UserDataRow} />
        </Table.Tbody>
      </Table>
      {!result.isLoading && result.data && (
        <Pagination
          total={result.data.page_count}
          value={args.page || 1}
          onChange={(page) => setArgs({ ...args, page })}
          mt="md"
          withEdges
          withControls
        />
      )}
    </Container>
  )
}

const ErrorState = ({ error }: { error: any }) => {
  useEffect(() => {
    const message = getAPIErrorMessage(error)
    showNotification({ type: 'error', title: 'Error loading users', message })
  }, [error])

  return (
    <Table.Tr>
      <td colSpan={99}>
        <Group justify="center" gap="xs" m="sm" c="red">
          <IconExclamationCircle />
          <Text>Could not load users</Text>
        </Group>
      </td>
    </Table.Tr>
  )
}

const LoadingState = () => (
  <Table.Tr>
    <td colSpan={99}>
      <Center m="sm">
        <Loader />
      </Center>
    </td>
  </Table.Tr>
)

const EmptyState = () => (
  <Table.Tr>
    <td colSpan={99}>
      <Center m="sm">No users found</Center>
    </td>
  </Table.Tr>
)

interface TableBodyProps {
  result: ReturnType<typeof useGetUsersQuery>
  dataRow: React.ComponentType<{ user: User }>
}

const TableBody = ({ result, dataRow }: TableBodyProps) => {
  if (result.isError) {
    return <ErrorState error={result.error} />
  }
  if (result.isLoading) {
    return <LoadingState />
  }

  const data: User[] = result.data?.results || []
  if (data.length < 1) {
    return <EmptyState />
  }

  const DataRow = dataRow
  return (
    <>
      {data.map((user) => (
        <DataRow key={user.id} user={user} />
      ))}
    </>
  )
}

const UserDataRow = ({ user }: { user: User }) => {
  return (
    <Table.Tr>
      <Table.Td>
        <Anchor href={user.url}>{user.full_name}</Anchor>
      </Table.Td>
      <Table.Td>{user.is_intern ? 'Intern' : 'Staff'}</Table.Td>
      <Table.Td>{user.email}</Table.Td>
      <Table.Td>{user.created_at}</Table.Td>
      <Table.Td>
        <GroupLabels
          groups={user.groups.value}
          isSuperUser={user.is_superuser}
        />
      </Table.Td>
      <Table.Td>
        <Center>
          {user.is_active ? (
            <IconCheck color="var(--mantine-color-green-6)" stroke={3} />
          ) : (
            <IconX color="var(--mantine-color-yellow-6)" stroke={3} />
          )}
        </Center>
      </Table.Td>
    </Table.Tr>
  )
}

mount(App)
