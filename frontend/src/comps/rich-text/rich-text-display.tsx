import { Link, RichTextEditor, RichTextEditorProps } from '@mantine/tiptap'
import { useEditor } from '@tiptap/react'
import StarterKit from '@tiptap/starter-kit'
import React, { useEffect } from 'react'

import '@mantine/core/styles.css'
import '@mantine/tiptap/styles.css'

interface RichTextDisplayProps
  extends Omit<RichTextEditorProps, 'editor' | 'children'> {
  content?: string
}

export const RichTextDisplay = ({
  content,
  ...props
}: RichTextDisplayProps) => {
  const editor = useEditor({
    extensions: [
      StarterKit,
      Link.configure({
        HTMLAttributes: {
          target: null,
        },
      }),
    ],
    editable: false,
  })

  useEffect(() => {
      editor?.commands.setContent(content ?? '')
  }, [editor, content])

  return (
    <RichTextEditor
      className="rich-text-display"
      editor={editor}
      styles={{ root: { border: 'none' } }}
      {...props}
    >
      <RichTextEditor.Content />
    </RichTextEditor>
  )
}
