import { useRichTextEditorContext } from '@mantine/tiptap'
import { Editor, RichTextArea } from 'comps/rich-text'
import React from 'react'
import { Button, Label, Popup } from 'semantic-ui-react'

interface CommentInputButtonProps {
  onSubmit: (editor: Editor) => void
}

const CommentInputButton = (props: CommentInputButtonProps) => {
  const { editor } = useRichTextEditorContext()

  editor.setOptions({
    editorProps: {
      handleDOMEvents: {
        keydown: (view, event) => {
          if (event.key === 'Enter' && event.ctrlKey) {
            event.preventDefault()
            props.onSubmit(editor)
          }
        },
      },
    },
  })

  const style: React.CSSProperties = {
    paddingBottom: '0.25rem',
    display: 'flex',
    flexDirection: 'row',
    justifyContent: 'flex-end',
    gap: '0.5rem',
  }

  return (
    <div style={style}>
      <Popup
        mouseEnterDelay={1000}
        trigger={
          <Button
            circular
            icon="arrow up"
            size="mini"
            type="button"
            onClick={() => props.onSubmit(editor)}
          />
        }
      >
        <Label size="mini">Ctrl</Label>
        <Label size="mini">Enter</Label> to submit comment
      </Popup>
    </div>
  )
}

interface CommentInputProps {
  autoFocus?: boolean
  children?: React.ReactNode
  disabled?: boolean
  onSubmit?: (editor: Editor) => void
  placeholder?: string
}

export const CommentInput = (props: CommentInputProps) => {
  return (
    <RichTextArea placeholder={props.placeholder}>
      {props.onSubmit && <CommentInputButton onSubmit={props.onSubmit} />}
    </RichTextArea>
  )
}
