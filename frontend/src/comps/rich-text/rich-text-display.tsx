import {
  RichTextEditor,
  RichTextEditorProps,
} from 'comps/rich-text/rich-text-editor'
import React from 'react'
import classes1 from './rich-text-display.module.css'
import { default as classes2 } from './prosemirror.module.css'

interface RichTextDisplayProps extends RichTextEditorProps {
  content?: string
}

export const RichTextDisplay = ({
  content,
  ...props
}: RichTextDisplayProps) => {
  return (
    <RichTextEditor
      {...props}
      disabled={true}
      initialContent={content}
      updateOnContentChange
      classNames={{
        content: `${classes1.content} ${classes2.content}`,
        root: classes1.root,
      }}
    />
  )
}
