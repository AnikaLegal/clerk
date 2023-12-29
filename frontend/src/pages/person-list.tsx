import React, { useState } from 'react'
import {
  Button,
  Container,
  Header,
  Table,
  Input,
  Loader,
} from 'semantic-ui-react'
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

  const isLoading = searchResults.isFetching || listResults.isFetching
  const people = (query ? searchResults.data : listResults.data) || []

  const search = debouncer(() => {
    searchQuery({ query }).catch((err) => {
      enqueueSnackbar(getAPIErrorMessage(err, 'Failed to search parties'), {
        variant: 'error',
      })
    })
  })
  useEffectLazy(() => search(), [query])
  return (
    <Container>
      <Header as="h1">Parties</Header>
      <a href={CONTEXT.create_url}>
        <Button primary>Add a party</Button>
      </a>
      <div style={{ margin: '1em 0' }}>
        <Input
          fluid
          icon="search"
          placeholder="Search by name, email, phone or address..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
      </div>
      <Loader active={listResults.isLoading} inline="centered">
        Loading...
      </Loader>
      <FadeTransition in={!isLoading}>
        <Table celled>
          <Table.Header>
            <Table.Row>
              <Table.HeaderCell>Name</Table.HeaderCell>
              <Table.HeaderCell>Email</Table.HeaderCell>
              <Table.HeaderCell>Address</Table.HeaderCell>
              <Table.HeaderCell>Phone number</Table.HeaderCell>
            </Table.Row>
          </Table.Header>
          <Table.Body>
            {people.length < 1 && (
              <Table.Row>
                <td>No people found</td>
              </Table.Row>
            )}
            {people.map((person) => (
              <Table.Row key={person.url}>
                <Table.Cell>
                  <a href={person.url}>{person.full_name}</a>
                </Table.Cell>
                <Table.Cell>{person.email}</Table.Cell>
                <Table.Cell>{person.address}</Table.Cell>
                <Table.Cell>{person.phone_number}</Table.Cell>
              </Table.Row>
            ))}
          </Table.Body>
        </Table>
      </FadeTransition>
    </Container>
  )
}

mount(App)
