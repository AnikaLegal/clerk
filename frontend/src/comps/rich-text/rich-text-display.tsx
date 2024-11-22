import { Link, RichTextEditor } from '@mantine/tiptap'
import { useEditor } from '@tiptap/react'
import StarterKit from '@tiptap/starter-kit'
import React, { useEffect } from 'react'
import { createGlobalStyle } from 'styled-components'

import '@mantine/core/styles.css'
import '@mantine/tiptap/styles.css'

interface RichTextDisplayProps {
  content?: string
}

/* An internal element of the text editor has padding, which we don't want, that
 * we cannot manipulate with component styling. This is a convenient way to
 * address that.
 */
const GlobalStyles = createGlobalStyle`
  .rich-text-display .tiptap.ProseMirror {
    padding: 0;
  }
`

export const RichTextDisplay = ({ content }: RichTextDisplayProps) => {
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
    editor?.commands.setContent(content)
  }, [editor, content])

  return (
    <RichTextEditor
      className="rich-text-display"
      editor={editor}
      styles={{ root: { border: 'none' } }}
    >
      <GlobalStyles />
      <RichTextEditor.Content />
    </RichTextEditor>
  )
}
