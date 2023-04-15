import React, { useState } from 'react'
import { Button, Container, Header, Table, Input } from 'semantic-ui-react'

import { mount, debounce, useEffectLazy } from 'utils'
import { api } from 'api'
import { FadeTransition } from 'comps/transitions'

import { Person } from 'types'

interface DjangoContext {
  people: Person[]
  create_url: string
}

const CONTEXT = (window as any).REACT_CONTEXT as DjangoContext

const debouncer = debounce(300)

const App = () => {
  const [isLoading, setIsLoading] = useState(false)
  const [people, setPeople] = useState(CONTEXT.people)
  const [query, setQuery] = useState('')
  const search = debouncer(() => {
    setIsLoading(true)
    api.person
      .search({ person: query })
      .then(({ data }) => {
        if (data) {
          setPeople(data)
        }
        setIsLoading(false)
      })
      .catch(() => setIsLoading(false))
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
