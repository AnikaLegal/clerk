import React, { useState } from "react";
import { Formik } from "formik";
import { Header, Form, Button, Message, Segment } from "semantic-ui-react";
import moment from "moment";

import { api } from "api";
import { MarkdownTextArea } from "comps/markdown-editor";

export const submitNote =
  (issue, setIssue, setNotes, setSuccess) =>
  (values, { setSubmitting, setErrors }) => {
    const note = { ...values };
    note.event = note.event
      ? moment.utc(values.event, "DD/MM/YYYY").format()
      : note.event;

    api.case.note.add(issue.id, note).then(({ resp, data }) => {
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
  };

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
        initialValues={{ text: "", note_type: "PARALEGAL" }}
        validate={({ text }) =>
          text ? null : { "File note text": "File note cannot be empty" }
        }
        onSubmit={submitNote(issue, setIssue, setNotes, setSuccess)}
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
            <MarkdownTextArea
              onChange={(e) => setFieldValue("text", e.target.value)}
              disabled={isSubmitting}
              rows={3}
              placeholder="Write case details here"
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
              Close
            </Button>
            <Message success>File note created</Message>
          </Form>
        )}
      </Formik>
    </Segment>
  );
};
