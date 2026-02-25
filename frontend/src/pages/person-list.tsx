import {
  Button,
  Center,
  Container,
  Grid,
  Group,
  Loader,
  Pagination,
  Table,
  Text,
  TextInput,
  Title,
} from '@mantine/core'
import { useDebouncedCallback } from '@mantine/hooks'
import { IconSearch } from '@tabler/icons-react'
import { GetPeopleApiArg, useGetPeopleQuery } from 'api'
import { useSnackbar } from 'notistack'
import React, { useEffect, useState } from 'react'
import { UserPermission } from 'types'
import { getAPIErrorMessage, mount } from 'utils'

interface DjangoContext {
  user: UserPermission
  create_url: string
}

const CONTEXT = (window as any).REACT_CONTEXT as DjangoContext

const App = () => {
  const [args, setArgs] = useState<GetPeopleApiArg>({ page: 1 })
  const { enqueueSnackbar } = useSnackbar()

  const handleFilterChange = useDebouncedCallback((value: string) => {
    setArgs({ page: 1, query: value })
  }, 300)

  const results = useGetPeopleQuery(args)

  useEffect(() => {
    if (results.error) {
      enqueueSnackbar(
        getAPIErrorMessage(results.error, 'Failed to load parties'),
        { variant: 'error' }
      )
    }
  }, [results.error])

  const isLoading = results.isFetching
  const people = results.data?.results || []
  const pageCount = results.data?.page_count || 1
  const total = results.data?.item_count || 0

  return (
    <Container size="xl">
      <Group wrap="nowrap" gap="sm" justify="space-between">
        <Title order={1}>
          <span>Parties</span>
        </Title>
        {CONTEXT.user.is_coordinator_or_better && (
          <Button component="a" href={CONTEXT.create_url} size="md">
            Add a party
          </Button>
        )}
      </Group>
      <Text c="dimmed">
        Showing {people.length} of {total} parties
      </Text>

      <Grid mt="lg">
        <Grid.Col>
          <TextInput
            label="Search"
            placeholder="Search by name, email, phone or address ..."
            rightSection={<IconSearch size={16} stroke={4} />}
            size="md"
            onChange={(e) => {
              handleFilterChange(e.target.value)
            }}
          />
        </Grid.Col>
      </Grid>

      {isLoading && (
        <Center style={{ minHeight: 40, marginTop: 20 }}>
          <Loader />
        </Center>
      )}

      <Table
        withColumnBorders
        withTableBorder
        verticalSpacing="xs"
        fz="md"
        mt="md"
      >
        <Table.Thead>
          <Table.Tr>
            <Table.Th>Name</Table.Th>
            <Table.Th>Email</Table.Th>
            <Table.Th>Address</Table.Th>
            <Table.Th>Phone number</Table.Th>
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>
          {people.length < 1 && (
            <Table.Tr>
              <td colSpan={99}>
                <Center m="sm">No people found</Center>
              </td>
            </Table.Tr>
          )}
          {people.map((person) => (
            <Table.Tr key={person.url}>
              <Table.Td>
                <a href={person.url}>{person.full_name}</a>
              </Table.Td>
              <Table.Td>{person.email}</Table.Td>
              <Table.Td>{person.address}</Table.Td>
              <Table.Td>{person.phone_number}</Table.Td>
            </Table.Tr>
          ))}
        </Table.Tbody>
      </Table>
      {!isLoading && people.length > 0 && (
        <Pagination
          total={pageCount}
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

mount(App)
