import React from 'react'
import { Button, Input, Dropdown, Form } from 'semantic-ui-react'

// Formik form component
export const DocumentTemplateForm = ({
  topicOptions,
  formik: { values, errors, handleSubmit, isSubmitting, setFieldValue },
}) => (
  <Form onSubmit={handleSubmit} error={Object.keys(errors).length > 0}>
    <div className={`field ${errors.topic && 'error'}`}>
      <label>Case Type</label>
      <Dropdown
        fluid
        selection
        placeholder="Select a case type"
        options={topicOptions}
        onChange={(e, { value }) => setFieldValue('topic', value)}
        value={values.topic}
      />
    </div>
    <div className={`field ${errors.files && 'error'}`}>
      <label>Files</label>
      <Input
        type="file"
        multiple
        name="files"
        onChange={(event) => {
          if (!event.currentTarget.files) return
          const files = Object.values(event.currentTarget.files).map(
            (file: File) => file
          )
          setFieldValue('files', files)
        }}
      />
    </div>
    {Object.entries(errors).map(([k, v]) => (
      <div key={k} className="ui error message">
        <div className="header">{k}</div>
        <p>{v}</p>
      </div>
    ))}
    <Button
      primary
      type="submit"
      disabled={isSubmitting}
      loading={isSubmitting}
    >
      Create document template
    </Button>
  </Form>
)
