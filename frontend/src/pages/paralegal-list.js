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

const { lawyers, paralegals } = window.REACT_CONTEXT;

const SEARCH_FIELDS = ["full_name", "email"];
const INTERN_OPTIONS = [
  { key: "Intern", value: "INTERN", text: "Intern" },
  { key: "Volunteer", value: "VOLUNTEER", text: "Volunteer" },
];

const searchFilter = (searchQuery) => (paralegal) =>
  SEARCH_FIELDS.some((fieldName) =>
    paralegal[fieldName].toLowerCase().includes(searchQuery.toLowerCase())
  );

const internFilter = (internQuery) => (paralegal) => {
  if (internQuery === "INTERN") return paralegal.is_intern;
  if (internQuery === "VOLUNTEER") return !paralegal.is_intern;
  return true;
};

const App = () => {
  const [search, setSearch] = useState("");
  const [intern, setIntern] = useState("");
  const paralegalResults =
    search || intern
      ? paralegals.filter(searchFilter(search)).filter(internFilter(intern))
      : paralegals;
  return (
    <Container>
      <Header as="h1">
        Lawyers
        <Header.Subheader>All users who are lawyers</Header.Subheader>
      </Header>
      <ParalegalTable accounts={lawyers} />

      <Header as="h1">
        Paralegals
        <Header.Subheader>
          All users who are paralegals or coordinators
        </Header.Subheader>
      </Header>
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
          placeholder="Find paralegals by name or email..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <Dropdown
          fluid
          selection
          clearable
          placeholder="Filter by intern status"
          options={INTERN_OPTIONS}
          onChange={(e, { value }) => setIntern(value)}
          value={intern}
        />
      </div>

      <ParalegalTable accounts={paralegalResults} />
    </Container>
  );
};

const ParalegalTable = ({ accounts }) => (
  <Table celled>
    <Table.Header>
      <Table.Row>
        <Table.HeaderCell>Name</Table.HeaderCell>
        <Table.HeaderCell textAlign="center">Latest Case</Table.HeaderCell>
        <Table.HeaderCell textAlign="center">Capacity (%)</Table.HeaderCell>
        <Table.HeaderCell textAlign="center">
          Total
          <br />
          Open
        </Table.HeaderCell>
        <Table.HeaderCell textAlign="center">
          Repairs
          <br />
          Open
        </Table.HeaderCell>
        <Table.HeaderCell textAlign="center">
          Bonds
          <br />
          Open
        </Table.HeaderCell>
        <Table.HeaderCell textAlign="center">
          Eviction
          <br />
          Open
        </Table.HeaderCell>
        <Table.HeaderCell textAlign="center">Total Cases</Table.HeaderCell>
      </Table.Row>
    </Table.Header>
    <Table.Body>
      {accounts.length < 1 && (
        <Table.Row>
          <td>No users found</td>
        </Table.Row>
      )}
      {accounts.map((u) => (
        <Table.Row key={u.url}>
          <Table.Cell>
            <a href={u.url}>
              {u.full_name}
              {u.is_intern && " (intern)"}
            </a>
          </Table.Cell>
          <Table.Cell textAlign="center">
            {u.latest_issue_created_at}
          </Table.Cell>
          <Table.Cell
            textAlign="center"
            className={getCapacityColor(u.capacity)}
          >
            {u.capacity < 0 ? "No capacity" : u.capacity}
          </Table.Cell>
          <Table.Cell textAlign="center">{u.open_cases}</Table.Cell>
          <Table.Cell textAlign="center">{u.open_repairs}</Table.Cell>
          <Table.Cell textAlign="center">{u.open_bonds}</Table.Cell>
          <Table.Cell textAlign="center">{u.open_eviction}</Table.Cell>
          <Table.Cell textAlign="center">{u.total_cases}</Table.Cell>
        </Table.Row>
      ))}
    </Table.Body>
  </Table>
);

const getCapacityColor = (capacity) => {
  if (capacity < 0) return "blue";
  if (capacity === 0) return "";
  if (capacity < 50) return "green";
  if (capacity < 75) return "yellow";
  if (capacity < 100) return "orange";
  return "red";
};

mount(App);
