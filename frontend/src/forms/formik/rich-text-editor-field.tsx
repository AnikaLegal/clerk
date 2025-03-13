import {
  EditorEvents,
  RichTextEditor,
  RichTextEditorProps,
} from 'comps/rich-text'
import { ErrorMessage, useField } from 'formik'
import React from 'react'
import { Form } from 'semantic-ui-react'

export interface RichTextEditorFieldProps extends RichTextEditorProps {
  name: string
  label?: string
  required?: boolean
}

export const RichTextEditorField = ({
  name,
  label,
  required,
  ...props
}: RichTextEditorFieldProps) => {
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
      {label && <label>{label}</label>}
      <RichTextEditor
        {...props}
        initialContent={meta.initialValue}
        onUpdate={handleUpdate}
      />
      <ErrorMessage name={name} />
    </Form.Field>
  )
}
