import React, { useState } from "react";
import { Button, Table } from "semantic-ui-react";
import { Formik } from "formik";

import { markdownToHtml } from "utils";
import { CaseListTable } from "comps/case-table";
import {
  AutoForm,
  getModelChoices,
  getModelInitialValues,
  FIELD_TYPES,
} from "comps/auto-form";

// Wrapper around AutoForm for updating a model or displating a table.
export const TableForm = ({
  fields,
  schema,
  model,
  setModel,
  modelName,
  onUpdate,
}) => {
  const [isEditMode, setEditMode] = useState(false);
  const toggleEditMode = () => setEditMode(!isEditMode);
  if (!isEditMode) {
    return (
      <>
        <FieldTable fields={fields} model={model} />
        <Button onClick={toggleEditMode}>Edit</Button>
      </>
    );
  }
  return (
    <Formik
      initialValues={getModelInitialValues(fields, model)}
      validationSchema={schema}
      onSubmit={(values, { setSubmitting, setErrors }) => {
        onUpdate(model.id, values).then(({ resp, data }) => {
          if (resp.status === 400) {
            setErrors(data);
          } else if (resp.ok) {
            setModel(data[modelName]);
            toggleEditMode();
          }
          setSubmitting(false);
        });
      }}
    >
      {(formik) => (
        <AutoForm
          fields={fields}
          choices={getModelChoices(fields, model)}
          formik={formik}
          onCancel={toggleEditMode}
          submitText="Update"
        />
      )}
    </Formik>
  );
};

const FieldTable = ({ fields, model }) => (
  <Table size="small" definition>
    <Table.Body>
      {fields.map(({ label, name, type }) => (
        <Table.Row key={label}>
          <Table.Cell width={3}>{label}</Table.Cell>
          {type === FIELD_TYPES.TEXTAREA ? (
            <td
              dangerouslySetInnerHTML={{
                __html: model[name] ? markdownToHtml(model[name]) : "-",
              }}
            />
          ) : (
            <Table.Cell>{getValueDisplay(model[name])}</Table.Cell>
          )}
        </Table.Row>
      ))}
    </Table.Body>
  </Table>
);

const getValueDisplay = (val) => {
  const t = typeof val;
  if (t === "undefined" || val === null || val === "") {
    return "-";
  }
  if (t === "object" && val && val.choices) {
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
