import { EditorEvents, RichTextArea, RichTextAreaProps } from 'comps/rich-text'
import { ErrorMessage, useField } from 'formik'
import React from 'react'
import { Form } from 'semantic-ui-react'

interface RichTextAreaFieldProps extends RichTextAreaProps {
  name: string
  label: string
  required?: boolean
}

export const RichTextAreaField = ({
  name,
  label,
  required,
  ...props
}: RichTextAreaFieldProps) => {
  const [, meta, helpers] = useField(name)

  const handleUpdate = ({ editor, transaction }: EditorEvents['update']) => {
    if (editor) {
      helpers.setValue(editor.getText() != '' ? editor.getHTML() : '')
      if (props.onUpdate) {
        props.onUpdate({ editor, transaction })
      }
    }
  }

  return (
    <Form.Field error={meta.touched && meta.error} required={required}>
      <label>{label}</label>
      <RichTextArea
        {...props}
        initialContent={meta.initialValue}
        onUpdate={handleUpdate}
      />
      <ErrorMessage name={name} />
    </Form.Field>
  )
}
