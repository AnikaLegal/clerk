import {
  RichTextEditor as MantineRichTextEditor,
  RichTextEditorProps as MantineRichTextEditorProps,
} from '@mantine/tiptap'
import Highlight from '@tiptap/extension-highlight'
import Placeholder from '@tiptap/extension-placeholder'
import TextAlign from '@tiptap/extension-text-align'
import { Editor, EditorEvents, Extensions, useEditor } from '@tiptap/react'
import { BubbleMenu } from '@tiptap/react/menus'
import StarterKit from '@tiptap/starter-kit'
import React, { useEffect } from 'react'
import { useEffectLazy } from 'utils'
import { CustomLink } from './extensions/rich-text-editor-link-fix'

import classes1 from './rich-text-editor.module.css'
import { default as classes2 } from './prosemirror.module.css'

export const RichTextToolbarFull = (
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

export const RichTextToolbarMinimal = (
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

export const RichTextBubbleMenuDefault = (editor: Editor) => {
  return (
    <BubbleMenu editor={editor}>
      <MantineRichTextEditor.ControlsGroup>
        <MantineRichTextEditor.Bold />
        <MantineRichTextEditor.Italic />
        <MantineRichTextEditor.Strikethrough />
        <MantineRichTextEditor.Link />
        <MantineRichTextEditor.OrderedList />
        <MantineRichTextEditor.BulletList />
        <MantineRichTextEditor.Blockquote />
      </MantineRichTextEditor.ControlsGroup>
    </BubbleMenu>
  )
}

export interface RichTextEditorProps
  extends Omit<MantineRichTextEditorProps, 'editor' | 'onBlur' | 'children'> {
  initialContent?: string
  updateOnContentChange?: boolean
  disabled?: boolean
  placeholder?: string
  onUpdate?: (update: EditorEvents['update']) => void
  onBlur?: (blur: EditorEvents['blur']) => void
  extensions?: Extensions // Allow custom extensions
  toolbar?: React.ReactNode
  bubbleMenu?: (editor: Editor) => React.ReactNode
}

export const RichTextEditor = ({
  variant = 'default',
  initialContent,
  updateOnContentChange = false,
  content,
  disabled,
  placeholder,
  onUpdate,
  onBlur,
  extensions,
  toolbar,
  bubbleMenu,
  ...props
}: RichTextEditorProps) => {
  const defaultExtensions: Extensions = [
    StarterKit.configure({
      link: false,
    }),
    Highlight,
    CustomLink.extend({ inclusive: false }).configure({
      defaultProtocol: 'https',
      HTMLAttributes: {
        target: null,
      },
      openOnClick: disabled,
    }),
    Placeholder.configure({ placeholder: placeholder }),
    TextAlign.configure({ types: ['heading', 'paragraph'] }),
  ]

  const editor = useEditor({
    shouldRerenderOnTransaction: true,
    extensions: extensions ?? defaultExtensions,
    /* We have to supply our own CSS that tiptap would have "injected" because
     * injected styles are removed when an editor is destroyed (e.g. in a modal)
     * even if other editors are still active.
     * See https://github.com/ueberdosis/tiptap/issues/6635.
     */
    injectCSS: false,
  })

  useEffect(() => {
    editor?.commands.setContent(initialContent ?? '', {
      emitUpdate: false,
      parseOptions: { preserveWhitespace: 'full' },
    })
  }, [editor])

  useEffectLazy(() => {
    if (updateOnContentChange) {
      editor?.commands.setContent(initialContent ?? '', {
        emitUpdate: false,
        parseOptions: { preserveWhitespace: 'full' },
      })
    }
  }, [initialContent])

  useEffect(() => {
    editor?.setEditable(!disabled, false)
  }, [editor, disabled])

  useEffect(() => {
    onUpdate ? editor?.on('update', onUpdate) : editor?.off('update')
  }, [editor, onUpdate])

  useEffect(() => {
    onBlur ? editor?.on('blur', onBlur) : editor?.off('blur')
  }, [editor, onBlur])

  return (
    <MantineRichTextEditor
      variant={variant}
      editor={editor}
      classNames={{
        content: `${classes1.content} ${classes2.content}`,
      }}
      {...props}
    >
      {toolbar && toolbar}
      {bubbleMenu && editor && bubbleMenu(editor)}
      <MantineRichTextEditor.Content />
    </MantineRichTextEditor>
  )
}
