import React, { useState } from "react";
import { Formik } from "formik";
import {
  Header,
  Form,
  Button,
  Message,
  Segment,
  Dropdown,
  Checkbox,
} from "semantic-ui-react";
import { DateInput } from "semantic-ui-calendar-react";
import moment from "moment";

import { submitCaseUpdate } from "./case-progress";
import { OUTCOMES } from "consts";

const OUTCOME_OPTIONS = Object.entries(OUTCOMES).map(([k, v]) => ({
  key: k,
  value: k,
  text: v,
}));

export const CloseForm = ({ issue, setIssue, setNotes, onCancel }) => {
  const [isSuccess, setSuccess] = useState(false);
  return (
    <Segment>
      <Header>Close the case.</Header>
      <p>
        Please make sure you correctly set all of the fields in this form. This
        data is crucial for our reporting and decision making.
      </p>
      <Formik
        initialValues={{
          is_open: false,
          stage: "CLOSED",
          outcome: issue.outcome,
          provided_legal_services: issue.provided_legal_services,
          outcome_notes: issue.outcome_notes,
        }}
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
              value={values.outcome}
              style={{ margin: "1em 0" }}
              loading={isSubmitting}
              placeholder="Select a case outcome"
              options={OUTCOME_OPTIONS}
              onChange={(e, { value }) =>
                setFieldValue("outcome", value, false)
              }
            />
            <textarea
              onChange={(e) => setFieldValue("outcome_notes", e.target.value)}
              disabled={isSubmitting}
              rows={3}
              value={values.outcome_notes}
              style={{ marginBottom: "1em" }}
              placeholder="Write outcome notes here"
            />
            <div style={{ margin: "0 0 1em 0" }}>
              <Checkbox
                label="Provided legal services"
                checked={values.provided_legal_services}
                onChange={(e, { checked }) =>
                  setFieldValue(
                    "provided_legal_services",
                    Boolean(checked),
                    false
                  )
                }
                disabled={isSubmitting}
              />
            </div>

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
              Close case
            </Button>
            <Button disabled={isSubmitting} onClick={onCancel}>
              Close
            </Button>
            <Message success>Case closed</Message>
          </Form>
        )}
      </Formik>
    </Segment>
  );
};
