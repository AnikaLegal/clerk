import { useFocusWithin } from '@mantine/hooks'
import { Link, RichTextEditor } from '@mantine/tiptap'
import Placeholder from '@tiptap/extension-placeholder'
import { ParseOptions } from '@tiptap/pm/model'
import { EditorEvents, useEditor } from '@tiptap/react'
import StarterKit from '@tiptap/starter-kit'
import React, { CSSProperties, useEffect } from 'react'

import '@mantine/core/styles.css'
import '@mantine/tiptap/styles.css'

interface RichTextAreaProps {
  initialContent?: string
  disabled?: boolean
  placeholder?: string
  onUpdate?: (update: EditorEvents['update']) => void
  onBlur?: (blur: EditorEvents['blur']) => void
}

export const RichTextArea = ({
  initialContent,
  disabled,
  placeholder,
  onUpdate,
  onBlur,
}: RichTextAreaProps) => {
  const editor = useEditor({
    extensions: [
      StarterKit,
      Link,
      Placeholder.configure({ placeholder: placeholder }),
    ],
  })

  useEffect(() => {
    const parseOptions: ParseOptions = {
      preserveWhitespace: 'full',
    }
    editor?.commands.setContent(initialContent, false, parseOptions)
  }, [editor])

  useEffect(() => {
    editor?.setEditable(!disabled, false)
  }, [editor, disabled])

  useEffect(() => {
    onUpdate ? editor?.on('update', onUpdate) : editor?.off('update')
  }, [editor, onUpdate])

  useEffect(() => {
    onBlur ? editor?.on('blur', onBlur) : editor?.off('blur')
  }, [editor, onBlur])

  /* Emulate semantic-ui-react focus styling to match other components for
   * the time being */
  const { ref, focused } = useFocusWithin()
  const focusedStyle: CSSProperties = {
    outline: '1px solid #85b7d9',
    borderRadius: 'var(--mantine-radius-default)',
  }

  return (
    <RichTextEditor
      ref={ref}
      editor={editor}
      styles={{ content: focused ? focusedStyle : {} }}
    >
      <RichTextEditor.Content />
    </RichTextEditor>
  )
}