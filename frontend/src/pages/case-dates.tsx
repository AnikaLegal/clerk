import React from 'react'
import { Container, Header } from 'semantic-ui-react'
import { mount } from 'utils'

interface DjangoContext {}
const CONTEXT = (window as any).REACT_CONTEXT as DjangoContext

const App = () => {
  return (
    <Container>
      <Header as="h1">
        Case Inbox
        <Header.Subheader></Header.Subheader>
      </Header>
    </Container>
  )
}

mount(App)
