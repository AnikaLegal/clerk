import React, { useState } from "react";
import { Formik } from "formik";
import { Header, Form, Button, Message, Segment } from "semantic-ui-react";

import { api } from "api";

export const FilenoteForm = ({ issue, setIssue, setNotes, onCancel }) => {
  const [isSuccess, setSuccess] = useState(false);
  return (
    <Segment>
      <Header>Add a file note</Header>
      <p>
        Leave a note of important case information, events or instructions. This
        note is visible to everybody who has access to the case.
      </p>
      <Formik
        initialValues={{ text: "" }}
        validate={({ text }) =>
          text ? null : { "File note text": "File note cannot be empty" }
        }
        onSubmit={(values, { setSubmitting, setErrors }) => {
          api.case.filenote
            .add(issue.id, values.text)
            .then(({ resp, data }) => {
              if (resp.status === 400) {
                setErrors(data);
              } else if (resp.ok) {
                setIssue(data.issue);
                setNotes(data.notes);
                setSuccess(true);
              } else {
                setErrors({
                  "Submission failure":
                    "We could not perform this action because something went wrong.",
                });
              }
              setSubmitting(false);
            });
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
