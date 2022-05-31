// Form framework
import React from "react";
import { DateInput } from "semantic-ui-calendar-react";
import { Button, Input, Form, Dropdown, TextArea } from "semantic-ui-react";
import { MarkdownTextArea } from "comps/markdown-editor";

import * as Yup from "yup";

export const FIELD_TYPES = {
  TEXT: "TEXT",
  EMAIL: "EMAIL",
  TEXTAREA: "TEXTAREA",
  DATE: "DATE",
  SINGLE_CHOICE: "SINGLE_CHOICE",
  MULTI_CHOICE: "MULTI_CHOICE",
  BOOL: "BOOL",
};

export const getFormSchema = (formFields) =>
  Yup.object().shape(
    formFields.reduce(
      (acc, val) =>
        val.schema
          ? {
              ...acc,
              [val.name]: val.schema,
            }
          : acc,
      {}
    )
  );

export const getModelChoices = (formFields, model) =>
  formFields.reduce((acc, field) => {
    const fieldVal = model[field.name];
    if (fieldVal && fieldVal.choices) {
      return { ...acc, [field.name]: fieldVal.choices };
    } else {
      return acc;
    }
  }, {});

export const getModelInitialValues = (formFields, model) =>
  formFields.reduce((acc, field) => {
    const fieldVal = model[field.name];
    const value = fieldVal.value ? fieldVal.value : fieldVal;
    return { ...acc, [field.name]: value };
  }, {});

const FieldSchema = Yup.array().of(
  Yup.object().shape({
    label: Yup.string().required(),
    name: Yup.string().required(),
    type: Yup.string().oneOf(Object.values(FIELD_TYPES)).required(),
    placeholder: Yup.string(),
    schema: Yup.object(),
  })
);

export const AutoForm = ({
  fields,
  choices,
  formik: {
    values,
    errors,
    touched,
    handleChange,
    handleSubmit,
    isSubmitting,
    setFieldValue,
  },
  onCancel = null,
  submitText = "Submit",
  cancelText = "Cancel",
}) => {
  FieldSchema.validateSync(fields);
  const labels = fields.reduce((acc, f) => ({ ...acc, [f.name]: f.label }), {});
  return (
    <Form onSubmit={handleSubmit} error={Object.keys(errors).length > 0}>
      {fields.map((f) => {
        const FieldComponent = FIELD_COMPONENTS[f.type];
        return (
          <Form.Field key={f.name} error={touched[f.name] && !!errors[f.name]}>
            <label>{f.label}</label>
            <FieldComponent
              {...f}
              value={values[f.name]}
              handleChange={handleChange}
              isSubmitting={isSubmitting}
              setFieldValue={setFieldValue}
              choices={choices[f.name]}
            />
          </Form.Field>
        );
      })}
      {Object.entries(errors).map(
        ([k, v]) =>
          touched[k] && (
            <div key={k} className="ui error message">
              <div className="header">{labels[k]}</div>
              <p>{v}</p>
            </div>
          )
      )}
      <Button
        primary
        type="submit"
        disabled={isSubmitting}
        loading={isSubmitting}
      >
        {submitText}
      </Button>
      {onCancel && (
        <Button
          disabled={isSubmitting}
          onClick={(e) => {
            e.preventDefault();
            onCancel();
          }}
        >
          {cancelText}
        </Button>
      )}
    </Form>
  );
};

const TextField = ({
  name,
  placeholder,
  value,
  handleChange,
  isSubmitting,
  type,
}) => (
  <Input
    placeholder={placeholder}
    value={value}
    name={name}
    onChange={handleChange}
    disabled={isSubmitting}
    type={type}
  />
);

const DateField = ({
  name,
  placeholder,
  value,
  setFieldValue,
  isSubmitting,
}) => (
  <DateInput
    placeholder={placeholder}
    value={value}
    name={name}
    dateFormat="DD/MM/YYYY"
    disabled={isSubmitting}
    autoComplete="off"
    onChange={(e, { name, value }) => setFieldValue(name, value, false)}
  />
);

const ChoiceField =
  (multiple) =>
  ({ name, placeholder, value, choices, setFieldValue, isSubmitting }) =>
    (
      <Dropdown
        fluid
        selection
        multiple={multiple}
        value={value}
        style={{ margin: "1em 0" }}
        placeholder={placeholder}
        disabled={isSubmitting}
        options={choices.map(([value, label]) => ({
          key: value,
          value: value,
          text: label,
        }))}
        onChange={(e, { value }) => setFieldValue(name, value, true)}
      />
    );

const BoolField = ({
  name,
  placeholder,
  value,
  setFieldValue,
  isSubmitting,
}) => (
  <Dropdown
    fluid
    selection
    value={value}
    style={{ margin: "1em 0" }}
    loading={isSubmitting}
    placeholder={placeholder}
    options={[
      {
        key: "Yes",
        text: "Yes",
        value: true,
      },
      {
        key: "No",
        text: "No",
        value: false,
      },
    ]}
    onChange={(e, { value }) => setFieldValue(name, value, false)}
  />
);

const TextAreaField = ({
  name,
  placeholder,
  value,
  handleChange,
  isSubmitting,
}) => (
  <MarkdownTextArea
    name={name}
    value={value}
    placeholder={placeholder}
    onChange={handleChange}
    disabled={isSubmitting}
  />
);

const FIELD_COMPONENTS = {
  TEXT: (props) => <TextField {...props} type="text" />,
  EMAIL: (props) => <TextField {...props} type="email" />,
  TEXTAREA: TextAreaField,
  DATE: DateField,
  BOOL: BoolField,
  SINGLE_CHOICE: ChoiceField(false),
  MULTI_CHOICE: ChoiceField(true),
};
