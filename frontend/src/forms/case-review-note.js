import React, { useState } from "react";
import { Formik } from "formik";
import { Header, Form, Button, Message, Segment } from "semantic-ui-react";
import { DateInput } from "semantic-ui-calendar-react";
import moment from "moment";

import { api } from "api";

export const ReviewForm = ({ issue, setIssue, setNotes, onCancel }) => {
  const [isSuccess, setSuccess] = useState(false);
  return (
    <Segment>
      <Header> Add a coordinator case review note</Header>
      <p>
        Leave a case review note for other coordinators to read. This note is
        not visible to paralegals.
      </p>
      <Formik
        initialValues={{ text: "", event: "" }}
        validate={({ text, event }) => {
          const errors = {};
          if (!text) errors.text = "File note cannot be empty";
          if (!event) errors.event = "Next review date is required";
          return errors;
        }}
        onSubmit={(values, { setSubmitting, setErrors }) => {
          setSubmitting(false);
          // Submit here
        }}
      >
        {({
          values,
          errors,
          handleChange,
          handleSubmit,
          isSubmitting,
          setFieldValue,
          setFieldTouched,
          touched,
        }) => (
          <Form
            onSubmit={handleSubmit}
            success={isSuccess}
            error={Object.keys(errors).length > 0}
          >
            <textarea
              onChange={(e) => setFieldValue("text", e.target.value, false)}
              disabled={isSubmitting}
              rows={3}
              value={values.text}
              style={{ marginBottom: "1em" }}
            />

            <DateInput
              name="event"
              dateFormat="DD/MM/YYYY"
              minDate={moment()}
              onChange={(e, { name, value }) =>
                setFieldValue(name, value, false)
              }
              value={values.event}
            />
            {Object.entries(errors)
              .filter(([k, v]) => touched[k])
              .map(([k, v]) => (
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
