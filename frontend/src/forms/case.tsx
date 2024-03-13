import { FormikProps } from 'formik'
import React from 'react'
import { Button, Input, Dropdown, Form } from 'semantic-ui-react'

interface CaseFormProps {
  create?: boolean
  editable?: boolean
  handleDelete?: (e: any) => void
  formik: FormikProps<any>
  topicOptions: string[][]
}

// Formik form component
export const CaseForm: React.FC<CaseFormProps> = ({
  create,
  editable,
  handleDelete,
  formik: {
    values,
    errors,
    handleChange,
    handleSubmit,
    isSubmitting,
    setFieldValue,
  },
  topicOptions,
}) => (
  <Form onSubmit={handleSubmit} error={Object.keys(errors).length > 0}>
    <div className={`field ${errors.support_contact_preferences && 'error'}`}>
      <label>Case topic</label>
      <Dropdown
        compact
        selection
        placeholder="Select case topic"
        onChange={(e, { value }) =>
          setFieldValue('topic', value)
        }
        options={topicOptions}
        disabled={!editable}
      />
    </div>
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
        {create ? 'Create case' : 'Update case'}
      </Button>
    ) : null}
    {!create && editable ? (
      <Button
        primary
        color="red"
        disabled={isSubmitting}
        loading={isSubmitting}
        onClick={handleDelete}
      >
        Delete
      </Button>
    ) : null}
  </Form>
)
