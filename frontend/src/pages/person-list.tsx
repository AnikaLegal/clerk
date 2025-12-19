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
import { useDebouncedCallback } from '@mantine/hooks'
import { IconSearch } from '@tabler/icons-react'
import { useSnackbar } from 'notistack'

import { mount, useEffectLazy, getAPIErrorMessage } from 'utils'
import { useGetPeopleQuery } from 'api'

import { FadeTransition } from 'comps/transitions'

interface DjangoContext {
  create_url: string
}

const CONTEXT = (window as any).REACT_CONTEXT as DjangoContext

const App = () => {
  const [query, setQuery] = useState('')
  const [page, setPage] = useState(1)
  const { enqueueSnackbar } = useSnackbar()

  const debouncedSetQueryAndPage = useDebouncedCallback(
    (value: string) => {
      // Batch into single state update and render
      setPage(1)
      setQuery(value)
    },
    300 // Debounce delay in milliseconds
  )

  const results = useGetPeopleQuery({ query: query || undefined, page })

  const isLoading = results.isFetching
  const people = results.data?.results || []
  const pageCount = results.data?.page_count || 1
  const total = results.data?.item_count || 0
  return (
    <Container size="xl" style={{ padding: '1.5rem 0' }}>
      <Title order={1}>Parties</Title>
      {!isLoading && (<Text mt={4} color="dimmed">Showing {people.length} of {total} parties</Text>)}
      <Button component="a" href={CONTEXT.create_url} size="md" mt="sm">
        Add a party
      </Button>
      <Grid mt="md">
        <Grid.Col span={6}>
          <TextInput
            placeholder="Search by name, email, phone or address ..."
            rightSection={<IconSearch size={16} stroke={4} />}
            size="md"
            onChange={(e) => {
              debouncedSetQueryAndPage(e.target.value)
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
      </FadeTransition>

      {pageCount > 1 && (
        <Center style={{ marginTop: 12 }}>
          <Pagination value={page} onChange={setPage} total={pageCount} />
        </Center>
      )}
    </Container>
  )
}

mount(App)