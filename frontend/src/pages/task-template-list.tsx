import React, { useState } from 'react'
import { Button, Container, Header, Table } from 'semantic-ui-react'
import { useSnackbar } from 'notistack'

import { mount } from 'utils'
import { FadeTransition } from 'comps/transitions'

interface DjangoContext {
  create_url: string
}

const CONTEXT = (window as any).REACT_CONTEXT as DjangoContext

const App = () => {
  const [isLoading, setIsLoading] = useState(false)
  const { enqueueSnackbar } = useSnackbar()

  return (
    <Container>
      <Header as="h1">Task Templates</Header>
      <a href={CONTEXT.create_url}>
        <Button primary>Create a new task template</Button>
      </a>
      <FadeTransition in={!isLoading}>
        <Table celled>
          <Table.Header>
            <Table.Row>
            </Table.Row>
          </Table.Header>
          <Table.Body></Table.Body>
        </Table>
      </FadeTransition>
    </Container>
  )
}

mount(App)
