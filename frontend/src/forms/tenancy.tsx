import React from 'react'
import { FormikProps } from 'formik'
import { Button, Input, Dropdown, Form } from 'semantic-ui-react'

import DateInput from 'comps/date-input'

interface TenancyFormProps {
  formik: FormikProps<any>
  isOnLeaseChoices: string[][]
  onCancel: () => void
}

// Formik form component
export const TenancyForm: React.FC<TenancyFormProps> = ({
  isOnLeaseChoices,
  onCancel,
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
    <div className={`field ${errors.address && 'error'}`}>
      <label>Address</label>
      <Input
        placeholder="123 Fake Street"
        value={values.address}
        name="address"
        onChange={handleChange}
      />
    </div>
    <div className={`field ${errors.suburb && 'error'}`}>
      <label>Suburb</label>
      <Input
        placeholder="Fakeington"
        value={values.suburb}
        name="suburb"
        onChange={handleChange}
      />
    </div>
    <div className={`field ${errors.postcode && 'error'}`}>
      <label>Postcode</label>
      <Input
        placeholder="1234"
        value={values.postcode}
        name="postcode"
        onChange={handleChange}
      />
    </div>

    <div className={`field ${errors.started && 'error'}`}>
      <label>Tenancy Start Date</label>
      <DateInput
        name="started"
        dateFormat="DD/MM/YYYY"
        autoComplete="off"
        placeholder="Select tenancy start date"
        onChange={(e, { name, value }) => setFieldValue(name, value)}
        value={values.started}
      />
    </div>

    <div className={`field ${errors.is_on_lease && 'error'}`}>
      <label>Is client on lease</label>
      <Dropdown
        fluid
        selection
        placeholder="Select whether the client is on the lease"
        options={isOnLeaseChoices.map(([value, display]) => ({
          key: value,
          value: value,
          text: display,
        }))}
        onChange={(e, { value }) => setFieldValue('is_on_lease', value)}
        value={values.is_on_lease}
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
      Update tenancy
    </Button>
    <Button type="button" onClick={onCancel} disabled={isSubmitting}>
      Cancel
    </Button>
  </Form>
)
