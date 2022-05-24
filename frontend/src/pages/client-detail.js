import React, { useState } from "react";
import { Container, Header, Button, Table } from "semantic-ui-react";

import { CaseListTable } from "comps/case-table";
import { ClientEditForm } from "forms/client-edit";
import { mount } from "utils";

const { client } = window.REACT_CONTEXT;

const App = () => {
  const [isEditMode, setEditMode] = useState(false);
  const toggleEditModel = () => {
    setEditMode(!isEditMode);
  };
  return (
    <Container>
      <Header as="h1">{client.full_name} (Client)</Header>
      {!isEditMode && <Button onClick={toggleEditModel}>Edit</Button>}
      {!isEditMode && <ClientDisplay client={client} />}
      {isEditMode && <ClientEditForm />}
    </Container>
  );
};

const ClientDisplay = ({ client }) => (
  <>
    <Header as="h3">Personal details</Header>
    <FieldTable
      client={client}
      fields={{
        "First name": client.first_name,
        "Last name": client.last_name,
        "Date of birth": client.date_of_birth,
        Gender: client.gender,
      }}
    />
    <Header as="h3">Contact details</Header>
    <FieldTable
      client={client}
      fields={{
        Email: client.email,
        "Phone number": client.phone_number,
        "Call times": client.call_times.display,
      }}
    />
    <Header as="h3">Other Information</Header>
    <FieldTable
      client={client}
      fields={{
        Referrer: client.referrer,
        "Referrer type": client.referrer_type.display,
        "Employment status": client.employment_status.display,
        "Special circumstances": client.special_circumstances.display,
        "Weekly income": client.weekly_income,
        "Primary language": client.primary_language,
        "Number of dependents": client.number_of_dependents,
        "Is Aboriginal or Torres Strait Islander":
          client.is_aboriginal_or_torres_strait_islander,
        "Legal access difficulties": client.legal_access_difficulties.display,
        "Rental circumstances": client.rental_circumstances.display,
        "Weekly rent": client.weekly_rent,
        "Is in a multi income household": client.is_multi_income_household,
      }}
    />
    <Header as="h3">Cases</Header>
    <CaseListTable issues={client.issue_set} />
  </>
);

const FieldTable = ({ client, fields }) => (
  <Table size="small" definition>
    <Table.Body>
      {Object.entries(fields).map(([key, val]) => (
        <Table.Row key={key}>
          <Table.Cell width={3}>{key}</Table.Cell>
          <Table.Cell>{getValueDisplay(val)}</Table.Cell>
        </Table.Row>
      ))}
    </Table.Body>
  </Table>
);

const getValueDisplay = (val) => {
  const t = typeof val;
  if (t === "undefined" || t === null || val === "") {
    return "-";
  }
  if (val === false) {
    return "No";
  }
  if (val === true) {
    return "Yes";
  }
  return val;
};

mount(App);
