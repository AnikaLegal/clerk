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
  const pageSize = 25

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

      <Center style={{ minHeight: 40 }}>
        {isLoading ? (
          <Loader />
        ) : (
          <Text color="dimmed">{`Showing ${pagedPeople.length} of ${total} parties`}</Text>
        )}
      </Center>

      <FadeTransition in={!isLoading}>
        <Table highlightOnHover verticalSpacing="md">
          <thead>
            <tr>
              <th>Name</th>
              <th>Email</th>
              <th>Address</th>
              <th>Phone number</th>
            </tr>
          </thead>
          <tbody>
            {total < 1 && (
              <tr>
                <td colSpan={4}>
                  <Text align="center">No people found</Text>
                </td>
              </tr>
            )}
            {pagedPeople.map((person) => (
              <tr key={person.url}>
                <td>
                  <a href={person.url}>{person.full_name}</a>
                </td>
                <td>{person.email}</td>
                <td>{person.address}</td>
                <td>{person.phone_number}</td>
              </tr>
            ))}
          </tbody>
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
