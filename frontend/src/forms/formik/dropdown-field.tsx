import { ErrorMessage, useField } from 'formik';
import React from 'react';
import { Dropdown, DropdownProps } from 'semantic-ui-react';

export const DropdownField = ({
  name,
  label,
  ...props
}: { name: string; label: string } & DropdownProps) => {
  const [field, meta, helpers] = useField(name)
  const handleChange = (e, data) => {
    helpers.setValue(data.value)
    if (props.onChange) {
      props.onChange(e, data)
    }
  }

  return (
    <div className={`field ${meta.touched && meta.error ? 'error' : ''}`}>
      <label>{label}</label>
      <Dropdown fluid selection {...field} {...props} onChange={handleChange} />
      <ErrorMessage name={name} />
    </div>
  )
}
