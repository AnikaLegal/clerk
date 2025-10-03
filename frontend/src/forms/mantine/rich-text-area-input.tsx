import { CSSProperties, Input, InputWrapperProps } from '@mantine/core'
import { useFocusWithin } from '@mantine/hooks'
import { EditorEvents, RichTextArea, RichTextAreaProps } from 'comps/rich-text'
import React from 'react'

export interface RichTextAreaInputProps
  extends Omit<InputWrapperProps, 'onChange'> {
  onChange?: (content: string) => void
  variant?: RichTextAreaProps['variant']
}

export const RichTextAreaInput = ({
  onChange,
  variant = 'subtle',
  ...props
}: RichTextAreaInputProps) => {
  const { ref, focused } = useFocusWithin()

  const handleUpdate = ({ editor }: EditorEvents['update']) => {
    if (onChange) {
      const content = editor.getText() != '' ? editor.getHTML() : ''
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
      <RichTextArea
        variant={variant}
        onUpdate={handleUpdate}
        initialContent={props.defaultValue?.toString()}
        styles={{ root: rootStyles }}
      />
    </Input.Wrapper>
  )
}
