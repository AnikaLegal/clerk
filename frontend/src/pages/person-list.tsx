import React, { useState } from 'react'
import {
  Button,
  Center,
  Container,
  Grid,
  Loader,
  Pagination,
  Table,
  Text,
  TextInput,
  Title,
} from '@mantine/core'
import type { TextInputProps } from '@mantine/core'
import { IconSearch } from '@tabler/icons-react'
import { useSnackbar } from 'notistack'

import { mount, debounce, useEffectLazy, getAPIErrorMessage } from 'utils'
import api, { useGetPeopleQuery } from 'api'

import { FadeTransition } from 'comps/transitions'

interface DjangoContext {
  create_url: string
}

const CONTEXT = (window as any).REACT_CONTEXT as DjangoContext

const debouncer = debounce(300)

const App = () => {
  const [query, setQuery] = useState('')
  const { enqueueSnackbar } = useSnackbar()
  const listResults = useGetPeopleQuery()
  const [searchQuery, searchResults] = api.useLazySearchPeopleQuery()

  // pagination state (client-side paging over the fetched people list)
  const [page, setPage] = useState(1)
  const pageSize = 14

  const isLoading = searchResults.isFetching || listResults.isFetching
  const people = (query ? searchResults.data : listResults.data) || []
  const total = people.length
  const pageCount = Math.max(1, Math.ceil(total / pageSize))
  const pagedPeople = people.slice((page - 1) * pageSize, page * pageSize)

  const search = debouncer(() => {
    searchQuery({ query }).catch((err) => {
      enqueueSnackbar(getAPIErrorMessage(err, 'Failed to search parties'), {
        variant: 'error',
      })
    })
  })
  useEffectLazy(() => search(), [query])
  return (
    <Container size="xl" style={{ padding: '1.5rem 0' }}>
      <Title order={1}>Parties</Title>
      {!isLoading && (<Text mt={4} color="dimmed">Showing {pagedPeople.length} of {total} parties</Text>)}
      <Button component="a" href={CONTEXT.create_url} size="md" mt="sm">
        Add a party
      </Button>
      <Grid mt="md">
        <Grid.Col span={6}>
          <TextInput
            placeholder="Search by name, email, phone or address ..."
            rightSection={<IconSearch size={16} stroke={4} />}
            size="md"
            value={query}
            onChange={(e) => {
              setQuery(e.target.value)
              setPage(1)
            }}
          />
        </Grid.Col>
      </Grid>

      {isLoading && (
        <Center style={{ minHeight: 40, marginTop: 20 }}>
          <Loader />
        </Center>
      )}

      <FadeTransition in={!isLoading}>
        <Table 
          withColumnBorders
          withTableBorder
          verticalSpacing="md"
          fz="md"
          mt="md">
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Name</Table.Th>
              <Table.Th>Email</Table.Th>
              <Table.Th>Address</Table.Th>
              <Table.Th>Phone number</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {total < 1 && (
              <Table.Tr>
                <Table.Td>
                  <Text align="center">No people found</Text>
                </Table.Td>
              </Table.Tr>
            )}
            {pagedPeople.map((person) => (
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
      </FadeTransition>

      {pageCount > 1 && (
        <Center style={{ marginTop: 12 }}>
          <Pagination page={page} onChange={setPage} total={pageCount} />
        </Center>
      )}
    </Container>
  )
}

mount(App)
