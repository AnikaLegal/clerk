import React, { useState } from "react";
import { Container, Header, Button } from "semantic-ui-react";
import * as Yup from "yup";

import { TableForm } from "comps/table-form";
import { getFormSchema, FIELD_TYPES } from "comps/auto-form";
import { CaseListTable } from "comps/case-table";
import { mount } from "utils";
import { api } from "api";

const App = () => {
  const [client, setClient] = useState(window.REACT_CONTEXT.client);
  return (
    <Container>
      <Header as="h1">{client.full_name} (Client)</Header>
      <Header as="h3">Personal details</Header>
      <TableForm
        fields={PERSONAL_FIELDS}
        schema={PERSONAL_SCHEMA}
        model={client}
        setModel={setClient}
        modelName="client"
        onUpdate={api.client.update}
      />
      <Header as="h3">Contact details</Header>
      <TableForm
        fields={CONTACT_FIELDS}
        schema={CONTACT_SCHEMA}
        model={client}
        setModel={setClient}
        modelName="client"
        onUpdate={api.client.update}
      />
      <Header as="h3">Other Information</Header>
      <TableForm
        fields={OTHER_FIELDS}
        schema={OTHER_SCHEMA}
        model={client}
        setModel={setClient}
        modelName="client"
        onUpdate={api.client.update}
      />
      <Header as="h3">Cases</Header>
      <CaseListTable issues={client.issue_set} fields={TABLE_FIELDS} />
    </Container>
  );
};

const TABLE_FIELDS = [
  "fileref",
  "topic",
  "paralegal",
  "lawyer",
  "created_at",
  "stage",
  "provided_legal_services",
  "outcome",
];

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
  {
    label: "Notes",
    type: FIELD_TYPES.TEXTAREA,
    name: "notes",
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
    schema: Yup.number().integer(),
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

<<<<<<< HEAD
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
      <CaseListTable issues={client.issue_set} fields={TABLE_FIELDS} />
    </Container>
  );
};

const ClientDetailsForm = ({ fields, schema, client, setClient }) => {
  const [isEditMode, setEditMode] = useState(false);
  const toggleEditMode = () => setEditMode(!isEditMode);
  if (!isEditMode) {
    return (
      <>
        <FieldTable fields={fields} client={client} />
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

const FieldTable = ({ fields, client }) => (
  <Table size="small" definition>
    <Table.Body>
      {fields.map(({ label, name, type }) => (
        <Table.Row key={label}>
          <Table.Cell width={3}>{label}</Table.Cell>
          {type === "TEXTAREA" ? (
            <td
              dangerouslySetInnerHTML={{
                __html: client[name] ? markdownToHtml(client[name]) : "-",
              }}
            />
          ) : (
            <Table.Cell>{getValueDisplay(client[name])}</Table.Cell>
          )}
        </Table.Row>
      ))}
    </Table.Body>
  </Table>
);

const getValueDisplay = (val) => {
  console.log(val);
  const t = typeof val;
  if (t === "undefined" || val === null || val === "") {
    return "-";
  }
  if (t === "object" && val.choices) {
    return val.display || "-";
  }
  if (val === false) {
    return "No";
  }
  if (val === true) {
    return "Yes";
  }
  return val;
};

=======
>>>>>>> Start account page react
mount(App);
