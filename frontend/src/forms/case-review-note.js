import React, { useState } from "react";
import { Formik } from "formik";
import { Header, Form, Button, Message, Segment } from "semantic-ui-react";
import { DateInput } from "semantic-ui-calendar-react";
import moment from "moment";

import { submitNote } from "./case-file-note";
import { TimelineNote } from "comps/timeline-item";
import { MarkdownExplainer } from "comps/markdown-editor";
import { TextArea } from "comps/textarea";

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
        initialValues={{ text: "", event: "", note_type: "REVIEW" }}
        validate={({ text, event }) => {
          const errors = {};
          if (!text) errors.text = "File note cannot be empty";
          if (!event) errors.event = "Next review date is required";
          return errors;
        }}
        onSubmit={submitNote(issue, setIssue, setNotes, setSuccess)}
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
            <TextArea
              onChange={(e) => setFieldValue("text", e.target.value, false)}
              disabled={isSubmitting}
              rows={3}
              value={values.text}
              style={{ marginBottom: "1em" }}
              placeholder="Write your review here (this is not a filenote, paralegals cannot see this)"
            />

            <DateInput
              name="event"
              dateFormat="DD/MM/YYYY"
              autoComplete="off"
              minDate={moment()}
              placeholder="Select a next review date"
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
              Close
            </Button>
            <Message success>File note created</Message>
            <MarkdownExplainer />
            <TimelineNote
              note={{
                note_type: values.note_type,
                created_at: "Now",
                event: values.event,
                text_display: values.text || "start typing...",
                creator: {
                  full_name: "You",
                },
              }}
            />
          </Form>
        )}
      </Formik>
    </Segment>
  );
};
