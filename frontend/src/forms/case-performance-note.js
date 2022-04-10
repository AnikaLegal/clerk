import React, { useState } from "react";
import { Formik } from "formik";
import { Header, Form, Button, Message, Segment } from "semantic-ui-react";
import { DateInput } from "semantic-ui-calendar-react";
import moment from "moment";

import { api } from "api";

export const PerformanceForm = ({ issue, setIssue, setNotes, onCancel }) => {
  const [isSuccess, setSuccess] = useState(false);
  return (
    <Segment>
      <Header> Add a paralegal performance review note</Header>
      <p>
        Leave a paralegal performance review note for{" "}
        {issue.paralegal.full_name}. This note is not visible to paralegals.
      </p>
      <Formik
        initialValues={{ text: "" }}
        validate={({ text }) =>
          text ? null : { "File note text": "File note cannot be empty" }
        }
        onSubmit={(values, { setSubmitting, setErrors }) => {
          // TODO
        }}
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
            <textarea
              onChange={(e) => setFieldValue("text", e.target.value)}
              disabled={isSubmitting}
              rows={3}
              value={values.text}
              style={{ marginBottom: "1em" }}
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
              Create note
            </Button>
            <Button disabled={isSubmitting} onClick={onCancel}>
              Cancel
            </Button>
            <Message success>File note created</Message>
          </Form>
        )}
      </Formik>
    </Segment>
  );
};
