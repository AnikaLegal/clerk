import { Box, Input, InputWrapperProps } from '@mantine/core'
import { RichTextEditorVariant } from '@mantine/tiptap/lib/RichTextEditor'
import {
  EditorEvents,
  RichTextEditor,
  RichTextEditorToolbar,
} from 'comps/rich-text'
import React from 'react'

export interface RichTextEditorInputProps
  extends Omit<InputWrapperProps, 'onChange'> {
  onChange?: (content: string) => void
  variant?: RichTextEditorVariant
  toolbar?: RichTextEditorToolbar
}

export const RichTextEditorInput = ({
  onChange,
  variant = 'subtle',
  toolbar = 'minimal',
  ...props
}: RichTextEditorInputProps) => {
  const handleUpdate = ({ editor }: EditorEvents['update']) => {
    const content = editor.getText() != '' ? editor.getHTML() : ''
    if (onChange) {
      onChange(content)
    }
  }

  return (
    <Input.Wrapper {...props}>
      <Box
        style={{
          marginTop: props.description
            ? 'calc(var(--mantine-spacing-xs) / 2)'
            : 0,
        }}
      >
        <RichTextEditor
          variant={variant}
          toolbar={toolbar}
          onUpdate={handleUpdate}
          initialContent={props.defaultValue?.toString()}
        />
      </Box>
    </Input.Wrapper>
  )
}
