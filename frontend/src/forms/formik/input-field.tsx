import { ErrorMessage, useField } from 'formik'
import React from 'react'
import { Input, InputProps } from 'semantic-ui-react'

export const InputField = ({
  name,
  label,
  ...props
}: { name: string; label: string } & InputProps) => {
  const [field, meta] = useField(name)

  return (
    <div className={`field ${meta.touched && meta.error ? 'error' : ''}`}>
      <label>{label}</label>
      <Input {...field} {...props} />
      <ErrorMessage name={name} />
    </div>
  )
}
