import React, { useState } from "react";
import {
  Button,
  Container,
  Header,
  Table,
  Input,
  Label,
  Dropdown,
} from "semantic-ui-react";

import { mount, debounce, useEffectLazy } from "utils";
import { api } from "api";
import { FadeTransition } from "comps/transitions";
import { GroupLabels } from "comps/group-label";
const CONTEXT = window.REACT_CONTEXT;
const GROUP_OPTIONS = [
  { key: "", value: "", text: "All groups" },
  { key: "Paralegal", value: "Paralegal", text: "Paralegal" },
  { key: "Coordinator", value: "Coordinator", text: "Coordinator" },
  { key: "Admin", value: "Admin", text: "Admin" },
];

const debouncer = debounce(300);

const App = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [users, setUsers] = useState(CONTEXT.users);
  const [name, setName] = useState("");
  const [group, setGroups] = useState("");
  const search = debouncer(() => {
    setIsLoading(true);
    api.accounts
      .search({ name, group })
      .then(({ data }) => {
        setUsers(data);
        setIsLoading(false);
      })
      .catch(() => setIsLoading(false));
  });
  useEffectLazy(() => search(), [name, group]);
  return (
    <Container>
      <Header as="h1">Accounts</Header>
      <a href={CONTEXT.create_url}>
        <Button primary>Invite a paralegal</Button>
      </a>
      <div
        style={{
          margin: "1rem 0",
          display: "grid",
          gap: "1rem",
          gridTemplateColumns: "1fr 1fr",
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
          onChange={(e, { value }) => setGroups(value)}
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
                <Table.Cell>{u.is_intern ? "Intern" : "Staff"}</Table.Cell>
                <Table.Cell>{u.email}</Table.Cell>
                <Table.Cell>{u.created_at}</Table.Cell>
                <Table.Cell>
                  <GroupLabels groups={u.groups} isSuperUser={u.is_superuser} />
                </Table.Cell>
              </Table.Row>
            ))}
          </Table.Body>
        </Table>
      </FadeTransition>
    </Container>
  );
};

mount(App);
