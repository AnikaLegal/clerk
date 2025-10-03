import { CSSProperties, Input, InputWrapperProps } from '@mantine/core'
import { useFocusWithin } from '@mantine/hooks'
import {
  EditorEvents,
  RichTextEditor,
  RichTextEditorProps,
} from 'comps/rich-text'
import React from 'react'

export interface RichTextEditorInputProps
  extends Omit<InputWrapperProps, 'onChange'> {
  onChange?: (content: string) => void
  variant?: RichTextEditorProps['variant']
  toolbar?: RichTextEditorProps['toolbar']
  bubbleMenu?: RichTextEditorProps['bubbleMenu']
}

export const RichTextEditorInput = ({
  onChange,
  variant = 'subtle',
  toolbar,
  bubbleMenu,
  ...props
}: RichTextEditorInputProps) => {
  const { ref, focused } = useFocusWithin()

  const handleUpdate = ({ editor }: EditorEvents['update']) => {
    const content = editor.getText() != '' ? editor.getHTML() : ''
    if (onChange) {
      onChange(content)
    }
  }

  const rootStyles: CSSProperties = {
    marginTop: props.description ? 'calc(var(--mantine-spacing-xs) / 2)' : 0,
    marginBottom: props.error ? 'calc(var(--mantine-spacing-xs) / 2)' : 0,
    border: props.error
      ? 'calc(0.0625rem * var(--mantine-scale)) solid var(--mantine-color-error)'
      : focused
        ? 'calc(0.0625rem * var(--mantine-scale)) solid var(--mantine-primary-color-filled)'
        : '',
    borderRadius: 'var(--mantine-radius-default)',
  }

  return (
    <Input.Wrapper size="md" ref={ref} {...props}>
      <RichTextEditor
        variant={variant}
        toolbar={toolbar}
        bubbleMenu={bubbleMenu}
        onUpdate={handleUpdate}
        initialContent={props.defaultValue?.toString()}
        styles={{ root: rootStyles }}
      />
    </Input.Wrapper>
  )
}
