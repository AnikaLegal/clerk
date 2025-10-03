import {
  RichTextEditor,
  RichTextEditorProps,
  RichTextBubbleMenuDefault,
} from 'comps/rich-text/rich-text-editor'
import React from 'react'

export interface RichTextAreaProps
  extends Omit<RichTextEditorProps, 'bubbleMenu' | 'toolbar'> {}

export const RichTextArea = (props: RichTextAreaProps) => {
  return <RichTextEditor bubbleMenu={RichTextBubbleMenuDefault} {...props} />
}
