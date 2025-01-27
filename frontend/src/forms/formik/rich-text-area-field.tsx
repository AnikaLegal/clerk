import { EditorEvents, RichTextArea, RichTextAreaProps } from 'comps/rich-text'
import { ErrorMessage, useField } from 'formik'
import React from 'react'

export const RichTextAreaField = ({
  name,
  label,
  ...props
}: { name: string; label: string } & RichTextAreaProps) => {
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
    <div className={`field ${meta.touched && meta.error ? 'error' : ''}`}>
      <label>{label}</label>
      <RichTextArea
        {...props}
        initialContent={meta.initialValue}
        onUpdate={handleUpdate}
      />
      <ErrorMessage name={name} />
    </div>
  )
}
