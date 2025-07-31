import { useFocusWithin } from '@mantine/hooks'
import {
  RichTextEditor as MantineRichTextEditor,
  RichTextEditorProps as MantineRichTextEditorProps,
} from '@mantine/tiptap'
import { RichTextEditorVariant } from '@mantine/tiptap/lib/RichTextEditor'
import Highlight from '@tiptap/extension-highlight'
import Placeholder from '@tiptap/extension-placeholder'
import TextAlign from '@tiptap/extension-text-align'
import Underline from '@tiptap/extension-underline'
import { ParseOptions } from '@tiptap/pm/model'
import { EditorEvents, Extension, useEditor } from '@tiptap/react'
import StarterKit from '@tiptap/starter-kit'
import React, { CSSProperties, ReactNode, useEffect } from 'react'
import { CustomLink } from './extensions/rich-text-editor-link-fix'

import '@mantine/core/styles.css'
import '@mantine/tiptap/styles.css'

export type RichTextEditorToolbar = 'full' | 'minimal' | ReactNode

export interface RichTextEditorProps
  extends Omit<MantineRichTextEditorProps, 'editor' | 'onBlur' | 'children'> {
  initialContent?: string
  disabled?: boolean
  placeholder?: string
  onUpdate?: (update: EditorEvents['update']) => void
  onBlur?: (blur: EditorEvents['blur']) => void
  extensions?: Extension[] // Allow custom extensions
  toolbar?: RichTextEditorToolbar
}

const RichTextToolbarFull = () => (
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
)

const RichTextToolbarMinimal = () => (
  <MantineRichTextEditor.Toolbar>
    <MantineRichTextEditor.ControlsGroup>
      <MantineRichTextEditor.Bold />
      <MantineRichTextEditor.Italic />
      <MantineRichTextEditor.Strikethrough />
    </MantineRichTextEditor.ControlsGroup>
    <MantineRichTextEditor.ControlsGroup>
      <MantineRichTextEditor.Link />
      <MantineRichTextEditor.OrderedList />
      <MantineRichTextEditor.BulletList />
    </MantineRichTextEditor.ControlsGroup>
    <MantineRichTextEditor.ControlsGroup>
      <MantineRichTextEditor.Blockquote />
    </MantineRichTextEditor.ControlsGroup>
  </MantineRichTextEditor.Toolbar>
)

export interface RichTextToolbarProps {
  toolbar?: RichTextEditorToolbar
}

export const RichTextToolbar = ({ toolbar = 'full' }: RichTextToolbarProps) => {
  return (
    <>
      {toolbar === 'full' ? (
        <RichTextToolbarFull />
      ) : toolbar === 'minimal' ? (
        <RichTextToolbarMinimal />
      ) : (
        toolbar
      )}
    </>
  )
}

export const RichTextEditor = ({
  variant = 'default',
  initialContent,
  disabled,
  placeholder,
  onUpdate,
  onBlur,
  extensions,
  toolbar,
}: RichTextEditorProps) => {
  const defaultExtensions: Extension[] = [
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
  ]

  const editor = useEditor({
    extensions: extensions ?? defaultExtensions,
  })

  useEffect(() => {
    const parseOptions: ParseOptions = {
      preserveWhitespace: 'full',
    }
    editor?.commands.setContent(initialContent ?? '', false, parseOptions)
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

  const { ref, focused } = useFocusWithin()
  const focusedStyle: CSSProperties = {
    outline: '1px solid #85b7d9',
    borderRadius: 'var(--mantine-radius-default)',
  }

  return (
    <MantineRichTextEditor
      variant={variant}
      editor={editor}
      ref={ref}
      styles={{ content: focused ? focusedStyle : {} }}
    >
      <RichTextToolbar toolbar={toolbar} />
      <MantineRichTextEditor.Content />
    </MantineRichTextEditor>
  )
}
