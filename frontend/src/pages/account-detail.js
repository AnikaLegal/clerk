import React, { useState } from "react";
import { Container, Header, Button, Tab } from "semantic-ui-react";
import * as Yup from "yup";

import { TimelineNote } from "comps/timeline-item";
import { TableForm } from "comps/table-form";
import { getFormSchema, FIELD_TYPES } from "comps/auto-form";
import { CaseListTable } from "comps/case-table";
import { mount } from "utils";
import { api } from "api";
import { AccountPermissions } from "comps/account-permissions";

const App = () => {
  const [account, setAccount] = useState(window.REACT_CONTEXT.account);
  let tabPanes = [
    {
      menuItem: "Paralegal cases",
      render: () => (
        <Tab.Pane>
          <CaseListTable issues={account.issue_set} fields={TABLE_FIELDS} />
        </Tab.Pane>
      ),
    },
    {
      menuItem: "Lawyer cases",
      render: () => (
        <Tab.Pane>
          <CaseListTable issues={account.lawyer_issues} fields={TABLE_FIELDS} />
        </Tab.Pane>
      ),
    },
    {
      menuItem: "Permissions",
      render: () => (
        <Tab.Pane>
          <AccountPermissions account={account} />
        </Tab.Pane>
      ),
    },
    {
      menuItem: "Performance notes",
      render: () => (
        <Tab.Pane>
          {account.performance_notes.length < 1 && "No notes yet"}
          {account.performance_notes.map((note) => (
            <TimelineNote note={note} key={note.id} />
          ))}
        </Tab.Pane>
      ),
    },
  ];
  // Prioritise lawyer issues if they exist
  if (account.lawyer_issues.length > 0) {
    tabPanes = [tabPanes[1], tabPanes[0], tabPanes[2], tabPanes[3]];
  }
  return (
    <Container>
      <Header as="h1">
        {account.full_name}
        <Header.Subheader>{account.email}</Header.Subheader>
      </Header>
      <Header as="h3">User details</Header>
      <TableForm
        fields={FIELDS}
        schema={SCHEMA}
        model={account}
        setModel={setAccount}
        modelName="account"
        onUpdate={api.accounts.update}
      />

      <Tab style={{ marginTop: "2em" }} panes={tabPanes} />
    </Container>
  );
};

const TABLE_FIELDS = [
  "fileref",
  "topic",
  "client",
  "paralegal",
  "lawyer",
  "created_at",
  "stage",
  "provided_legal_services",
  "outcome",
];

const FIELDS = [
  {
    label: "First name",
    schema: Yup.string().required("Required"),
    type: FIELD_TYPES.TEXT,
    name: "first_name",
  },
  {
    label: "Last name",
    schema: Yup.string().required("Required"),
    type: FIELD_TYPES.TEXT,
    name: "last_name",
  },
  {
    label: "Is Intern",
    name: "is_intern",
    type: FIELD_TYPES.BOOL,
    schema: Yup.string().required("Required"),
  },
  {
    label: "Case capacity",
    type: FIELD_TYPES.TEXT,
    name: "case_capacity",
    schema: Yup.number().integer().positive(),
  },
];
const SCHEMA = getFormSchema(FIELDS);

mount(App);
