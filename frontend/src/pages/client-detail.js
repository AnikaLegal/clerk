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

const PERSONAL_FIELDS = [
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
];
const CONTACT_FIELDS = [
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
];
const OTHER_FIELDS = [
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
const PERSONAL_SCHEMA = getFormSchema(PERSONAL_FIELDS);
const CONTACT_SCHEMA = getFormSchema(CONTACT_FIELDS);
const OTHER_SCHEMA = getFormSchema(OTHER_FIELDS);

const App = () => {
  const [client, setClient] = useState(window.REACT_CONTEXT.client);
  return (
    <Container>
      <Header as="h1">{client.full_name} (Client)</Header>
      <Header as="h3">Personal details</Header>
      <ClientDetailsForm
        fields={PERSONAL_FIELDS}
        schema={PERSONAL_SCHEMA}
        client={client}
        setClient={setClient}
      />
      <Header as="h3">Contact details</Header>
      <ClientDetailsForm
        fields={CONTACT_FIELDS}
        schema={CONTACT_SCHEMA}
        client={client}
        setClient={setClient}
      />
      <Header as="h3">Other Information</Header>
      <ClientDetailsForm
        fields={OTHER_FIELDS}
        schema={OTHER_SCHEMA}
        client={client}
        setClient={setClient}
      />
      <Header as="h3">Cases</Header>
      <CaseListTable issues={client.issue_set} />
    </Container>
  );
};

const ClientDetailsForm = ({ fields, schema, client, setClient }) => {
  const [isEditMode, setEditMode] = useState(false);
  const toggleEditMode = () => setEditMode(!isEditMode);
  if (!isEditMode) {
    return (
      <>
        <FieldTable fields={fields.map((f) => [f.label, client[f.name]])} />
        <Button onClick={toggleEditMode}>Edit</Button>
      </>
    );
  }
  return (
    <Formik
      initialValues={getModelInitialValues(fields, client)}
      validationSchema={schema}
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
          fields={fields}
          choices={getModelChoices(fields, client)}
          formik={formik}
          onCancel={toggleEditMode}
          submitText="Update"
        />
      )}
    </Formik>
  );
};

const FieldTable = ({ fields }) => (
  <Table size="small" definition>
    <Table.Body>
      {fields.map(([label, value]) => (
        <Table.Row key={label}>
          <Table.Cell width={3}>{label}</Table.Cell>
          <Table.Cell>{getValueDisplay(value)}</Table.Cell>
        </Table.Row>
      ))}
    </Table.Body>
  </Table>
);

const getValueDisplay = (val) => {
  const t = typeof val;
  if (t === "object" && val.display) {
    return val.display;
  }
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
