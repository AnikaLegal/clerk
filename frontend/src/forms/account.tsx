import React from 'react'
import { Button, Input, Dropdown, Form } from 'semantic-ui-react'
import { FormikProps } from 'formik'

interface AccountFormProps {
  formik: FormikProps<any>
}

// Formik form component
export const AccountForm: React.FC<AccountFormProps> = ({
  formik: { values, errors, handleChange, handleSubmit, isSubmitting },
}) => (
  <Form onSubmit={handleSubmit} error={Object.keys(errors).length > 0}>
    <div className={`field ${errors.first_name && 'error'}`}>
      <label>Full Name</label>
      <Input
        placeholder="Jane"
        value={values.first_name}
        name="first_name"
        onChange={handleChange}
        disabled={isSubmitting}
      />
    </div>
    <div className={`field ${errors.last_name && 'error'}`}>
      <label>Full Name</label>
      <Input
        placeholder="Doe"
        value={values.last_name}
        name="last_name"
        onChange={handleChange}
        disabled={isSubmitting}
      />
    </div>
    <div className={`field ${errors.email && 'error'}`}>
      <label>Email</label>
      <Input
        placeholder="jane.doe@anikalegal.com"
        value={values.email}
        name="email"
        onChange={handleChange}
        disabled={isSubmitting}
      />
    </div>

    {Object.entries(errors).map(([k, v]) => (
      <div key={k} className="ui error message">
        <div className="header">{k}</div>
        <p>{v as string}</p>
      </div>
    ))}
    <Button
      primary
      type="submit"
      disabled={isSubmitting}
      loading={isSubmitting}
    >
      Invite
    </Button>
  </Form>
)
