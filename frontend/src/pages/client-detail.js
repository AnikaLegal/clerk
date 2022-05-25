import React, { useState } from "react";
import { Container, Header, Button, Table } from "semantic-ui-react";
import { Formik } from "formik";
import * as Yup from "yup";

import { CaseListTable } from "comps/case-table";
import {
  AutoForm,
  getModelChoices,
  getModelInitialValues,
  getFormSchema,
  FIELD_TYPES,
} from "comps/auto-form";
import { mount } from "utils";
import { api } from "api";

const FORM_FIELDS = [
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
    label: "Gender",
    name: "gender",
    type: FIELD_TYPES.SINGLE_CHOICE,
    schema: Yup.string().required("Required"),
  },
  {
    label: "Date of birth",
    type: FIELD_TYPES.DATE,
    name: "date_of_birth",
  },
  {
    label: "Email",
    type: FIELD_TYPES.TEXT,
    name: "email",
    schema: Yup.string().email().required("Required"),
  },
  {
    label: "Phone number",
    name: "phone_number",
    type: FIELD_TYPES.TEXT,
    schema: Yup.string().required("Required"),
  },
  {
    label: "Call times",
    type: FIELD_TYPES.MULTI_CHOICE,
    name: "call_times",
  },
  {
    label: "Referrer",
    name: "referrer",
    type: FIELD_TYPES.TEXT,
    schema: Yup.string(),
  },
  {
    label: "Referrer type",
    type: FIELD_TYPES.SINGLE_CHOICE,
    name: "referrer_type",
  },
  {
    label: "Special circumstances",
    type: FIELD_TYPES.MULTI_CHOICE,
    name: "special_circumstances",
  },
  {
    label: "Primary language",
    name: "primary_language",
    schema: Yup.string(),
    type: FIELD_TYPES.TEXT,
  },
  {
    label: "Is Aboriginal or Torres Strait Islander",
    name: "is_aboriginal_or_torres_strait_islander",
    schema: Yup.bool(),
    type: FIELD_TYPES.BOOL,
  },
  {
    label: "Legal access difficulties",
    type: FIELD_TYPES.MULTI_CHOICE,
    name: "legal_access_difficulties",
  },
  {
    label: "Rental circumstances",
    type: FIELD_TYPES.SINGLE_CHOICE,
    name: "rental_circumstances",
  },
  {
    label: "Employment status",
    schema: Yup.array().of(Yup.string()).required("Required"),
    type: FIELD_TYPES.MULTI_CHOICE,
    name: "employment_status",
  },
  {
    label: "Weekly income",
    name: "weekly_income",
    schema: Yup.number().integer().positive(),
    type: FIELD_TYPES.TEXT,
  },
  {
    label: "Weekly rent",
    name: "weekly_rent",
    schema: Yup.number().integer().positive(),
    type: FIELD_TYPES.TEXT,
  },
  {
    label: "Number of dependents",
    name: "number_of_dependents",
    schema: Yup.number().integer().positive(),
    type: FIELD_TYPES.TEXT,
  },
  {
    label: "Is in a multi income household",
    name: "is_multi_income_household",
    schema: Yup.bool(),
    type: FIELD_TYPES.BOOL,
  },
];

const FORM_SCHEMA = getFormSchema(FORM_FIELDS);

const App = () => {
  const [isEditMode, setEditMode] = useState(false);
  const [client, setClient] = useState(window.REACT_CONTEXT.client);
  const toggleEditMode = () => {
    2;
    setEditMode(!isEditMode);
  };
  return (
    <Container>
      <Header as="h1">{client.full_name} (Client)</Header>
      {!isEditMode && <Button onClick={toggleEditMode}>Edit</Button>}
      {!isEditMode && <ClientDisplay client={client} />}
      {isEditMode && (
        <Formik
          initialValues={getModelInitialValues(FORM_FIELDS, client)}
          validationSchema={FORM_SCHEMA}
          onSubmit={(values, { setSubmitting, setErrors }) => {
            api.client.update(client.id, values).then(({ resp, data }) => {
              if (resp.status === 400) {
                setErrors(data);
              } else if (resp.ok) {
                setClient(data.client);
                toggleEditMode();
              }
              setSubmitting(false);
            });
          }}
        >
          {(formik) => (
            <AutoForm
              fields={FORM_FIELDS}
              choices={getModelChoices(FORM_FIELDS, client)}
              formik={formik}
              onCancel={toggleEditMode}
              submitText="Update client"
            />
          )}
        </Formik>
      )}
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
        Gender: client.gender.display,
        "Date of birth": client.date_of_birth,
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
        "Special circumstances": client.special_circumstances.display,
        "Primary language": client.primary_language,
        "Is Aboriginal or Torres Strait Islander":
          client.is_aboriginal_or_torres_strait_islander,
        "Legal access difficulties": client.legal_access_difficulties.display,
        "Rental circumstances": client.rental_circumstances.display,
        "Employment status": client.employment_status.display,
        "Weekly income": client.weekly_income,
        "Weekly rent": client.weekly_rent,
        "Number of dependents": client.number_of_dependents,
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
