import api, { GetUsersApiArg, User } from 'api'
import { GroupLabels } from 'comps/group-label'
import { FadeTransition } from 'comps/transitions'
import React, { useState } from 'react'
import {
  Button,
  Container,
  Dropdown,
  Form,
  Header,
  Icon,
  Input,
  Table,
} from 'semantic-ui-react'
import { mount, useDebounce } from 'utils'

interface DjangoContext {
  create_url: string
  groups: string[]
  user: User
}
const CONTEXT = (window as any).REACT_CONTEXT as DjangoContext

const App = () => {
  const [args, setArgs] = useState<GetUsersApiArg>({})
  const debounced = useDebounce(args, 300)
  const userResults = api.useGetUsersQuery(debounced)

  const users = userResults.data || []

  const updateArgs = (name: keyof GetUsersApiArg, value) => {
    var updated = {}
    if (value === null || value === '') {
      const { [name]: _, ...remaining } = args
      updated = remaining
    } else {
      updated = { ...args, [name]: value }
    }
    setArgs(updated)
  }

  return (
    <Container>
      <Header as="h1">Accounts</Header>
      {CONTEXT.user.is_coordinator_or_better && (
        <a href={CONTEXT.create_url}>
          <Button primary style={{ marginBottom: '1rem' }}>
            Invite a paralegal
          </Button>
        </a>
      )}
      <Form>
        <Form.Group widths="equal">
          <Form.Field>
            <Input
              icon="search"
              placeholder="Search names..."
              value={args.name}
              onChange={(e, { value }) => updateArgs('name', value)}
            />
          </Form.Field>
          <Form.Field>
            <Dropdown
              clearable
              fluid
              selection
              placeholder="Filter groups"
              options={CONTEXT.groups.map((value) => ({
                key: value,
                value: value,
                text: value,
              }))}
              value={args.group}
              onChange={(e, { value }) => updateArgs('group', value)}
            />
          </Form.Field>
          <Form.Field>
            <Dropdown
              clearable
              fluid
              selection
              placeholder="Active?"
              options={[
                { key: 'yes', value: true, text: 'Yes' },
                { key: 'no', value: false, text: 'No' },
              ]}
              value={args.isActive}
              onChange={(e, { value }) => updateArgs('isActive', value)}
            />
          </Form.Field>
        </Form.Group>
      </Form>
      <FadeTransition in={!userResults.isLoading}>
        <Table celled>
          <Table.Header>
            <Table.Row>
              <Table.HeaderCell>Name</Table.HeaderCell>
              <Table.HeaderCell>Org</Table.HeaderCell>
              <Table.HeaderCell>Email</Table.HeaderCell>
              <Table.HeaderCell>Created</Table.HeaderCell>
              <Table.HeaderCell>Permissions</Table.HeaderCell>
              <Table.HeaderCell>Active?</Table.HeaderCell>
            </Table.Row>
          </Table.Header>
          <Table.Body>
            {users.length < 1 && (
              <Table.Row>
                <td>No users found</td>
              </Table.Row>
            )}
            {users.map((u) => (
              <Table.Row key={u.url}>
                <Table.Cell>
                  <a href={u.url}>{u.full_name}</a>
                </Table.Cell>
                <Table.Cell>{u.is_intern ? 'Intern' : 'Staff'}</Table.Cell>
                <Table.Cell>{u.email}</Table.Cell>
                <Table.Cell>{u.created_at}</Table.Cell>
                <Table.Cell>
                  <GroupLabels groups={u.groups} isSuperUser={u.is_superuser} />
                </Table.Cell>
                <Table.Cell>
                  {u.is_active ? (
                    <Icon name="check" color="green" />
                  ) : (
                    <Icon name="times" color="grey" />
                  )}
                </Table.Cell>
              </Table.Row>
            ))}
          </Table.Body>
        </Table>
      </FadeTransition>
    </Container>
  )
}

mount(App)
