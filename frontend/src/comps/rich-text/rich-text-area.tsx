import { useFocusWithin } from '@mantine/hooks'
import { RichTextEditor } from '@mantine/tiptap'
import Highlight from '@tiptap/extension-highlight'
import Placeholder from '@tiptap/extension-placeholder'
import Underline from '@tiptap/extension-underline'
import { ParseOptions } from '@tiptap/pm/model'
import { BubbleMenu, EditorEvents, useEditor } from '@tiptap/react'
import StarterKit from '@tiptap/starter-kit'
import React, { CSSProperties, useEffect } from 'react'
import { CustomLink } from './extensions/rich-text-editor-link-fix'

import '@mantine/core/styles.css'
import '@mantine/tiptap/styles.css'

interface RichTextAreaProps {
  autoFocus?: boolean
  children?: React.ReactNode
  disabled?: boolean
  initialContent?: string
  onBlur?: (blur: EditorEvents['blur']) => void
  onUpdate?: (update: EditorEvents['update']) => void
  placeholder?: string
}

export const RichTextArea = (props: RichTextAreaProps) => {
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
      Placeholder.configure({ placeholder: props.placeholder }),
      Underline,
    ],
  })

  useEffect(() => {
    const parseOptions: ParseOptions = {
      preserveWhitespace: 'full',
    }
    editor?.commands.setContent(props.initialContent, false, parseOptions)
  }, [editor])

  useEffect(() => {
    editor?.setEditable(!props.disabled, false)
  }, [editor, props.disabled])

  useEffect(() => {
    props.onUpdate
      ? editor?.on('update', props.onUpdate)
      : editor?.off('update')
  }, [editor, props.onUpdate])

  useEffect(() => {
    props.onBlur ? editor?.on('blur', props.onBlur) : editor?.off('blur')
  }, [editor, props.onBlur])

  useEffect(() => {
    if (props.autoFocus) {
      editor?.commands.focus()
    }
  }, [editor, props.autoFocus])

  /* Emulate semantic-ui-react focus styling to match other components for
   * the time being */
  const { ref, focused } = useFocusWithin()
  const focusedStyle: CSSProperties = {
    borderColor: '#85b7d9',
  }

  return (
    <RichTextEditor
      ref={ref}
      editor={editor}
      styles={{ root: focused ? focusedStyle : {} }}
    >
      {editor && (
        <BubbleMenu editor={editor}>
          <RichTextEditor.ControlsGroup>
            <RichTextEditor.Bold />
            <RichTextEditor.Italic />
            <RichTextEditor.Underline />
            <RichTextEditor.Highlight />
            <RichTextEditor.Link />
            <RichTextEditor.Unlink />
          </RichTextEditor.ControlsGroup>
        </BubbleMenu>
      )}
      <RichTextEditor.Content />
      {props.children && props.children}
    </RichTextEditor>
  )
}
