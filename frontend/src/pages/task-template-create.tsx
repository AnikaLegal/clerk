import React from 'react'
import { Container, Header } from 'semantic-ui-react'
import { useSnackbar } from 'notistack'
import { mount } from 'utils'

interface DjangoContext {}

const CONTEXT = (window as any).REACT_CONTEXT as DjangoContext

const App = () => {
  const { enqueueSnackbar } = useSnackbar()

  return (
    <Container>
      <Header as="h1">Create a new task template</Header>
    </Container>
  )
}

mount(App)
