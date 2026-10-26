import { Anchor, Container, Text, Title } from '@mantine/core'
import { InviteForm } from 'features/invite'
import React from 'react'
import { mount } from 'utils'

interface DjangoContext {
  accounts_url: string
  group_values: string[]
  workspace_domain: string
}
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const CONTEXT = (window as any).REACT_CONTEXT as DjangoContext

const App = () => (
  <Container size="md">
    <Title order={1}>Invite users</Title>
    <Anchor href={CONTEXT.accounts_url} size="sm">
      Back to accounts
    </Anchor>
    <Text c="dimmed" mt="xs" mb="md">
      Creates a Clerk account and Microsoft 365 login, and emails the sign-in
      details. Microsoft access can take up to 15 minutes.
    </Text>
    <InviteForm
      groups={CONTEXT.group_values}
      workspaceDomain={CONTEXT.workspace_domain}
      accountsUrl={CONTEXT.accounts_url}
    />
  </Container>
)

mount(App)
