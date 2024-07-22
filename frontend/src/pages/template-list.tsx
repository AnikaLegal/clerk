import React from 'react'
import { Container, Header, List, Icon } from 'semantic-ui-react'

import { mount } from 'utils'

interface DjangoContext {
  email_url: string
  doc_url: string
  notify_url: string
  task_url: string
}

const { email_url, doc_url, notify_url, task_url } = (window as any)
  .REACT_CONTEXT as DjangoContext

const App = () => {
  return (
    <Container>
      <Header as="h1">Templates</Header>
      <List size="large" relaxed divided>
        <List.Item>
          <Icon name="envelope outline" style={{ verticalAlign: 'middle' }} />
          <List.Content>
            <a className="header" href={email_url}>
              Email templates
            </a>
            <List.Description>
              Common emails sent by paralegals
            </List.Description>
          </List.Content>
        </List.Item>
        <List.Item>
          <Icon name="file outline" style={{ verticalAlign: 'middle' }} />
          <List.Content>
            <a className="header" href={doc_url}>
              Document templates
            </a>
            <List.Description>
              Documents automatically added to every new case{' '}
            </List.Description>
          </List.Content>
        </List.Item>
        <List.Item>
          <Icon name="bell outline" style={{ verticalAlign: 'middle' }} />
          <List.Content>
            <a className="header" href={notify_url}>
              Notification templates
            </a>
            <List.Description>
              Notifications that are sent in response to case events{' '}
            </List.Description>
          </List.Content>
        </List.Item>
        <List.Item>
          <Icon name="tasks" style={{ verticalAlign: 'middle' }} />
          <List.Content>
            <a className="header" href={task_url}>
              Task templates
            </a>
            <List.Description>
              Tasks that are created in response to case events{' '}
            </List.Description>
          </List.Content>
        </List.Item>
      </List>
    </Container>
  )
}

mount(App)
