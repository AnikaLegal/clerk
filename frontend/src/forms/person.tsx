import { FormikProps } from 'formik'
import React from 'react'
import { Button, Input, Dropdown, Form } from 'semantic-ui-react'

const CONTACT_OPTIONS = [
  {
    key: 'EMPTY',
    value: '',
    text: '-',
  },

  {
    key: 'DIRECT_ONLY',
    value: 'DIRECT_ONLY',
    text: 'Contact me directly instead of the renter',
  },
  {
    key: 'COPY_ME_IN',
    value: 'COPY_ME_IN',
    text: 'Contact the renter directly but copy me into every interaction',
  },
  {
    key: 'PERIODIC_UPDATE',
    value: 'PERIODIC_UPDATE',
    text: 'Contact the renter directly but give me a fortnightly update',
  },
  {
    key: 'FINAL_UPDATE',
    value: 'FINAL_UPDATE',
    text: 'Contact the renter directly and give me an update only once the matter is finalised.',
  },
  {
    key: 'RENTER_MIA',
    value: 'RENTER_MIA',
    text: "Contact the renter directly but you may contact me if you can't contact the renter.",
  },
]

interface PersonFormProps {
  create?: boolean
  editable?: boolean
  handleDelete?: (e: any) => void
  formik: FormikProps<any>
}

// Formik form component
export const PersonForm: React.FC<PersonFormProps> = ({
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
}) => (
  <Form onSubmit={handleSubmit} error={Object.keys(errors).length > 0}>
    <div className={`field ${errors.full_name && 'error'}`}>
      <label>Full name</label>
      <Input
        placeholder="Jane Doe"
        value={values.full_name}
        name="full_name"
        onChange={handleChange}
        disabled={!editable}
      />
    </div>
    <div className={`field ${errors.email && 'error'}`}>
      <label>Email</label>
      <Input
        placeholder="jane.doe@example.com"
        value={values.email}
        name="email"
        onChange={handleChange}
        disabled={!editable}
      />
    </div>
    <div className={`field ${errors.address && 'error'}`}>
      <label>Address</label>
      <Input
        placeholder="123 Fake Street"
        value={values.address}
        name="address"
        onChange={handleChange}
        disabled={!editable}
      />
    </div>

    <div className={`field ${errors.phone_number && 'error'}`}>
      <label>Phone number</label>
      <Input
        placeholder="04123456"
        value={values.phone_number}
        name="phone_number"
        onChange={handleChange}
        disabled={!editable}
      />
    </div>
    <div className={`field ${errors.support_contact_preferences && 'error'}`}>
      <label>Contact preferences (support workers only)</label>
      <Dropdown
        fluid
        selection
        placeholder="Select contact preferences"
        options={CONTACT_OPTIONS}
        onChange={(e, { value }) =>
          setFieldValue('support_contact_preferences', value)
        }
        value={values.support_contact_preferences}
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
        {create ? 'Create person' : 'Update person'}
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
