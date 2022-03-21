import React from "react";
import { Formik } from "formik";
import { Container, Header } from "semantic-ui-react";

import { mount } from "utils";
import { api } from "api";
import { EmailTemplateForm } from "forms/email-template";

const CONTEXT = window.REACT_CONTEXT;

const App = () => (
  <Container>
    <Header as="h1">Email template</Header>
    <Formik
      initialValues={{
        topic: CONTEXT.template.topic,
        name: CONTEXT.template.name,
        subject: CONTEXT.template.subject,
        text: CONTEXT.template.text,
        html: "",
      }}
      validate={(values) => {}}
      onSubmit={(values, { setSubmitting, setErrors }) => {
        api.templates.email
          .update(CONTEXT.template.id, values)
          .then(({ resp, data }) => {
            if (resp.status === 400) {
              setErrors(data);
            }
            setSubmitting(false);
          });
      }}
    >
      {(formik) => (
        <EmailTemplateForm
          formik={formik}
          create={false}
          editable={CONTEXT.editable}
        />
      )}
    </Formik>
  </Container>
);

mount(App);
