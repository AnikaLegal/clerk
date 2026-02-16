import React, { useEffect, useState } from 'react'
import {
  Container,
  Group,
  Title,
  Button,
  Grid,
  Table,
  Center,
  Loader,
  Text,
  Anchor,
} from '@mantine/core'
import { IconCheck, IconExclamationCircle, IconX } from '@tabler/icons-react'
import { GetUsersApiArg, useGetUsersQuery, User } from 'api'
import { GroupLabels } from 'comps/group-label'
import { getAPIErrorMessage, mount } from 'utils'
import { UserPermission } from 'types'
import { SelectFilter, TextInputFilter } from 'comps/filter'
import { showNotification } from 'comps/notification'

interface DjangoContext {
  user: UserPermission
  create_url: string
  group_values: string[]
}
const CONTEXT = (window as any).REACT_CONTEXT as DjangoContext

const App = () => {
  const [args, setArgs] = useState<GetUsersApiArg>({
    sort: '-date_joined',
    isActive: true,
  })
  const result = useGetUsersQuery(args)

  const handleFilterChange = (key, value) => {
    setArgs((prevArgs) => ({
      ...prevArgs,
      [key]: value !== null ? value : undefined,
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

  const data: User[] = result.data || []
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
