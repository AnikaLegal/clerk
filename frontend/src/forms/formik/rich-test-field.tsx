import {
    EditorEvents,
    RichTextEditor,
    RichTextEditorProps,
} from 'comps/rich-text';
import { ErrorMessage, useField } from 'formik';
import React from 'react';

export const RichTextField = ({
  name,
  label,
  ...props
}: { name: string; label: string } & RichTextEditorProps) => {
  const [, meta, helpers] = useField(name)

  const handleUpdate = ({ editor, transaction }: EditorEvents['update']) => {
    if (editor) {
      helpers.setValue(editor.getHTML())
      if (props.onUpdate) {
        props.onUpdate({ editor, transaction })
      }
    }
  }

  return (
    <div className={`field ${meta.touched && meta.error ? 'error' : ''}`}>
      <label>{label}</label>
      <RichTextEditor
        {...props}
        initialContent={meta.initialValue}
        onUpdate={handleUpdate}
      />
      <ErrorMessage name={name} />
    </div>
  )
}
