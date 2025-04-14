import React, { useState } from 'react'
import {
  Button,
  Container,
  Header,
  Table,
  Icon,
  Input,
  Dropdown,
} from 'semantic-ui-react'

import { mount, debounce, useEffectLazy } from 'utils'
import { FadeTransition } from 'comps/transitions'
import { GroupLabels } from 'comps/group-label'
import api, { User } from 'api'

interface DjangoContext {
  users: User[]
  create_url: string
}

const CONTEXT = (window as any).REACT_CONTEXT as DjangoContext

const GROUP_OPTIONS = [
  { key: '', value: '', text: 'All groups' },
  { key: 'Paralegal', value: 'Paralegal', text: 'Paralegal' },
  { key: 'Coordinator', value: 'Coordinator', text: 'Coordinator' },
  { key: 'Lawyer', value: 'Lawyer', text: 'Lawyer' },
  { key: 'Admin', value: 'Admin', text: 'Admin' },
]

const debouncer = debounce(300)

const App = () => {
  const [isLoading, setIsLoading] = useState(false)
  const [users, setUsers] = useState<User[]>(CONTEXT.users)
  const [name, setName] = useState<string>('')
  const [group, setGroups] = useState<string>('')
  const [getUsers] = api.useLazyGetUsersQuery()

  const search = debouncer(() => {
    setIsLoading(true)
    getUsers({ name, group })
      .unwrap()
      .then((users) => {
        setUsers(users)
        setIsLoading(false)
      })
      .catch(() => setIsLoading(false))
  })
  useEffectLazy(() => search(), [name, group])
  return (
    <Container>
      <Header as="h1">Accounts</Header>
      <a href={CONTEXT.create_url}>
        <Button primary>Invite a paralegal</Button>
      </a>
      <div
        style={{
          margin: '1rem 0',
          display: 'grid',
          gap: '1rem',
          gridTemplateColumns: '1fr 1fr',
        }}
      >
        <Input
          icon="search"
          placeholder="Search names..."
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
        <Dropdown
          fluid
          selection
          placeholder="Filter groups"
          options={GROUP_OPTIONS}
          onChange={(e, { value }) => setGroups(String(value))}
          value={group}
        />
      </div>
      <FadeTransition in={!isLoading}>
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
