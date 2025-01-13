import { useFocusWithin } from '@mantine/hooks'
import { RichTextEditor as MantineRichTextEditor } from '@mantine/tiptap'
import Highlight from '@tiptap/extension-highlight'
import Placeholder from '@tiptap/extension-placeholder'
import TextAlign from '@tiptap/extension-text-align'
import Underline from '@tiptap/extension-underline'
import { ParseOptions } from '@tiptap/pm/model'
import { EditorEvents, useEditor } from '@tiptap/react'
import StarterKit from '@tiptap/starter-kit'
import React, { CSSProperties, useEffect } from 'react'
import { CustomLink } from './extensions/rich-text-editor-link-fix'

import '@mantine/core/styles.css'
import '@mantine/tiptap/styles.css'

export interface RichTextEditorProps {
  initialContent?: string
  disabled?: boolean
  placeholder?: string
  onUpdate?: (update: EditorEvents['update']) => void
  onBlur?: (blur: EditorEvents['blur']) => void
}

export const RichTextEditor = ({
  initialContent,
  disabled,
  placeholder,
  onUpdate,
  onBlur,
}: RichTextEditorProps) => {
  const editor = useEditor({
    extensions: [
      StarterKit,
      CustomLink.extend({ inclusive: false }).configure({
        defaultProtocol: 'https',
        HTMLAttributes: {
          target: null,
        },
        openOnClick: false,
      }),
      Highlight,
      Placeholder.configure({ placeholder: placeholder }),
      TextAlign.configure({ types: ['heading', 'paragraph'] }),
      Underline,
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
    <MantineRichTextEditor
      editor={editor}
      ref={ref}
      styles={{ content: focused ? focusedStyle : {} }}
    >
      <MantineRichTextEditor.Toolbar>
        <MantineRichTextEditor.ControlsGroup>
          <MantineRichTextEditor.Undo />
          <MantineRichTextEditor.Redo />
        </MantineRichTextEditor.ControlsGroup>

        <MantineRichTextEditor.ControlsGroup>
          <MantineRichTextEditor.Bold />
          <MantineRichTextEditor.Italic />
          <MantineRichTextEditor.Underline />
          <MantineRichTextEditor.Strikethrough />
          <MantineRichTextEditor.Highlight />
          <MantineRichTextEditor.ClearFormatting />
        </MantineRichTextEditor.ControlsGroup>

        <MantineRichTextEditor.ControlsGroup>
          <MantineRichTextEditor.H1 />
          <MantineRichTextEditor.H2 />
          <MantineRichTextEditor.H3 />
          <MantineRichTextEditor.H4 />
        </MantineRichTextEditor.ControlsGroup>

        <MantineRichTextEditor.ControlsGroup>
          <MantineRichTextEditor.Blockquote />
          <MantineRichTextEditor.Hr />
          <MantineRichTextEditor.BulletList />
          <MantineRichTextEditor.OrderedList />
        </MantineRichTextEditor.ControlsGroup>

        <MantineRichTextEditor.ControlsGroup>
          <MantineRichTextEditor.Link />
          <MantineRichTextEditor.Unlink />
        </MantineRichTextEditor.ControlsGroup>

        <MantineRichTextEditor.ControlsGroup>
          <MantineRichTextEditor.AlignLeft />
          <MantineRichTextEditor.AlignCenter />
          <MantineRichTextEditor.AlignJustify />
          <MantineRichTextEditor.AlignRight />
        </MantineRichTextEditor.ControlsGroup>
      </MantineRichTextEditor.Toolbar>

      <MantineRichTextEditor.Content />
    </MantineRichTextEditor>
  )
}
