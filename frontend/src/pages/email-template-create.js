import React, { useState } from "react";
import {
  Button,
  Container,
  Header,
  Table,
  Input,
  Dropdown,
  TextArea,
  Segment,
  Form,
} from "semantic-ui-react";
import { Formik } from "formik";

import { mount } from "utils";
import { api } from "api";
import { FadeTransition } from "comps/transitions";
import { MarkdownEditor } from "comps/markdown-editor";

const CONTEXT = window.REACT_CONTEXT;
const TOPIC_OPTIONS = [
  { key: "REPAIRS", value: "REPAIRS", text: "Repairs" },
  { key: "BONDS", value: "BONDS", text: "Bonds" },
  { key: "EVICTION", value: "EVICTION", text: "Eviction" },
];

const App = () => (
  <Container>
    <Header as="h1">Create a new email template</Header>
    <Formik
      initialValues={{
        topic: "",
        name: "",
        subject: "",
        text: "",
        html: "",
      }}
      validate={(values) => {}}
      onSubmit={(values, { setSubmitting }) => {
        setTimeout(() => {
          alert(JSON.stringify(values, null, 2));
          setSubmitting(false);
        }, 400);
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
        <Form onSubmit={handleSubmit}>
          <div className="field">
            <label>Case Type</label>
            <Dropdown
              fluid
              selection
              placeholder="Select a case type"
              options={TOPIC_OPTIONS}
              onChange={(e, { value }) => setFieldValue("topic", value)}
              value={values.topic}
            />
          </div>
          <div className="field">
            <label>Name</label>
            <Input
              placeholder="Template name"
              value={values.name}
              name="name"
              onChange={handleChange}
            />
          </div>
          <div className="field">
            <label>Subject</label>
            <Input
              placeholder="Template subject"
              value={values.subject}
              name="subject"
              onChange={handleChange}
            />
          </div>
          <MarkdownEditor
            text={values.text}
            html={values.html}
            onChangeText={(text) => setFieldValue("text", text)}
            onChangeHtml={(html) => setFieldValue("html", html)}
          />
          <Button
            primary
            type="submit"
            disabled={isSubmitting}
            loading={isSubmitting}
          >
            Create email template
          </Button>
        </Form>
      )}
    </Formik>
  </Container>
);

mount(App);
