import React from 'react'
import { Container, Header } from 'semantic-ui-react'
import { useSnackbar } from 'notistack'
import { mount } from 'utils'

interface DjangoContext {
  list_url: string
}

const { list_url } = (window as any).REACT_CONTEXT as DjangoContext

const App = () => {
  const { enqueueSnackbar } = useSnackbar()

  const onDelete = (e) => {
    e.preventDefault()
  }
  return (
    <Container>
      <Header as="h1">
        Edit task template
        <Header.Subheader>
          <a href={list_url}>Back to task templates</a>
        </Header.Subheader>
      </Header>
    </Container>
  )
}
mount(App)
