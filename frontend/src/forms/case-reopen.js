import React, { useState } from "react";
import { Formik } from "formik";
import {
  Header,
  Form,
  Button,
  Message,
  Segment,
  Dropdown,
} from "semantic-ui-react";
import * as Yup from "yup";

import { submitCaseUpdate } from "./case-progress";
import { STAGES } from "consts";

const STAGE_OPTIONS = Object.entries(STAGES)
  .filter(([k, v]) => k !== "CLOSED")
  .map(([k, v]) => ({
    key: k,
    value: k,
    text: v,
  }));

const FormSchema = Yup.object().shape({
  stage: Yup.string().required("Required"),
});

export const ReopenForm = ({ issue, setIssue, setNotes, onCancel }) => {
  const [isSuccess, setSuccess] = useState(false);
  return (
    <Segment>
      <Header>Re-open the case.</Header>
      <Formik
        initialValues={{
          is_open: true,
          stage: "",
        }}
        validationSchema={FormSchema}
        onSubmit={submitCaseUpdate(issue, setIssue, setSuccess)}
      >
        {({
          values,
          errors,
          handleChange,
          handleSubmit,
          isSubmitting,
          setFieldValue,
        }) => (
          <Form
            onSubmit={handleSubmit}
            success={isSuccess}
            error={Object.keys(errors).length > 0}
          >
            <Dropdown
              fluid
              selection
              search
              value={values.stage}
              style={{ margin: "1em 0" }}
              loading={isSubmitting}
              placeholder="Select a case stage"
              options={STAGE_OPTIONS}
              onChange={(e, { value }) => setFieldValue("stage", value, false)}
            />
            {Object.entries(errors).map(([k, v]) => (
              <Message error key={k}>
                <div className="header">{k}</div>
                <p>{v}</p>
              </Message>
            ))}
            <Button
              loading={isSubmitting}
              disabled={isSubmitting}
              positive
              type="submit"
            >
              Re-open case.
            </Button>
            <Button disabled={isSubmitting} onClick={onCancel}>
              Close
            </Button>
            <Message success>Case re-opened</Message>
          </Form>
        )}
      </Formik>
    </Segment>
  );
};
