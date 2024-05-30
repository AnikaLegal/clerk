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
import api, { useGetTasksQuery } from 'api'

import { FadeTransition } from 'comps/transitions'

interface DjangoContext {
}

const CONTEXT = (window as any).REACT_CONTEXT as DjangoContext

const debouncer = debounce(300)

const App = () => {
  const [query, setQuery] = useState('')
  const { enqueueSnackbar } = useSnackbar()
  const listResults = useGetTasksQuery()

  const isLoading = listResults.isFetching
  const tasks = listResults.data || []

  return (
    <Container>
      <Header as="h1">Tasks</Header>
      <Loader active={listResults.isLoading} inline="centered">
        Loading...
      </Loader>
      <FadeTransition in={!isLoading}>
        <Table celled>
          <Table.Header>
            <Table.Row>
              <Table.HeaderCell>Name</Table.HeaderCell>
              <Table.HeaderCell>Description</Table.HeaderCell>
            </Table.Row>
          </Table.Header>
          <Table.Body>
            {tasks.length < 1 && (
              <Table.Row>
                <td>No tasks found</td>
              </Table.Row>
            )}
            {tasks.map((task) => (
              <Table.Row key={task.url}>
                <Table.Cell>
                  <a href={task.url}>{task.name}</a>
                </Table.Cell>
                <Table.Cell>{task.description}</Table.Cell>
              </Table.Row>
            ))}
          </Table.Body>
        </Table>
      </FadeTransition>
    </Container>
  )
}

mount(App)
