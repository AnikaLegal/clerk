import React, { useState } from "react";
import {
  Button,
  Table,
  Input,
  Dropdown,
  TextArea,
  Segment,
  Form,
} from "semantic-ui-react";

import { MarkdownEditor } from "comps/markdown-editor";

const TOPIC_OPTIONS = [
  { key: "GENERAL", value: "GENERAL", text: "General" },
  { key: "REPAIRS", value: "REPAIRS", text: "Repairs" },
  { key: "BONDS", value: "BONDS", text: "Bonds" },
  { key: "EVICTION", value: "EVICTION", text: "Eviction" },
];

// Formik form component
export const EmailTemplateForm = ({
  create,
  editable,
  formik: {
    values,
    errors,
    handleChange,
    handleSubmit,
    isSubmitting,
    setFieldValue,
  },
}) => (
  <Form onSubmit={handleSubmit} error={Object.keys(errors).length > 0}>
    <div className={`field ${errors.topic && "error"}`}>
      <label>Case Type</label>
      <Dropdown
        fluid
        selection
        placeholder="Select a case type"
        options={TOPIC_OPTIONS}
        onChange={(e, { value }) => setFieldValue("topic", value)}
        value={values.topic}
        disabled={!editable}
      />
    </div>
    <div className={`field ${errors.name && "error"}`}>
      <label>Name</label>
      <Input
        placeholder="Template name"
        value={values.name}
        name="name"
        onChange={handleChange}
        disabled={!editable}
      />
    </div>
    <div className={`field ${errors.subject && "error"}`}>
      <label>Subject</label>
      <Input
        placeholder="Template subject"
        value={values.subject}
        name="subject"
        onChange={handleChange}
        disabled={!editable}
      />
    </div>
    <MarkdownEditor
      text={values.text}
      html={values.html}
      onChangeText={(text) => setFieldValue("text", text)}
      onChangeHtml={(html) => setFieldValue("html", html)}
      disabled={!editable}
    />
    {Object.entries(errors).map(([k, v]) => (
      <div key={k} className="ui error message">
        <div className="header">{k}</div>
        <p>{v}</p>
      </div>
    ))}
    {editable ? (
      <Button
        primary
        type="submit"
        disabled={isSubmitting}
        loading={isSubmitting}
      >
        {create ? "Create email template" : "Update email template"}
      </Button>
    ) : null}
  </Form>
);
