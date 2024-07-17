import React, { useState, useRef, useEffect } from 'react'
import { Color } from '@tiptap/extension-color'
import ListItem from '@tiptap/extension-list-item'
import TextStyle from '@tiptap/extension-text-style'
import Placeholder from '@tiptap/extension-placeholder'
import Underline from '@tiptap/extension-underline'
import Link from '@tiptap/extension-link'
import Highlight from '@tiptap/extension-highlight'
import { useEditor, EditorContent, Editor, JSONContent } from '@tiptap/react'
import StarterKit from '@tiptap/starter-kit'
import { Button, Segment, Popup, Modal, Form, Input } from 'semantic-ui-react'
import { NodePos } from '@tiptap/react'

// icon:highlighter | Fontawesome https://fontawesome.com/ | Fontawesome
export function IconHighlighter(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg viewBox="0 0 576 512" fill="currentColor" {...props}>
      <path d="M331 315l158.4-215-29.3-29.4L245 229l86 86zm-187 5v-71.7c0-15.3 7.2-29.6 19.5-38.6L436.6 8.4C444 2.9 453 0 462.2 0c11.4 0 22.4 4.5 30.5 12.6l54.8 54.8c8.1 8.1 12.6 19 12.6 30.5 0 9.2-2.9 18.2-8.4 25.6l-201.3 273c-9 12.3-23.4 19.5-38.6 19.5H240l-25.4 25.4c-12.5 12.5-32.8 12.5-45.3 0l-50.7-50.7c-12.5-12.5-12.5-32.8 0-45.3L144 320zM23 466.3l63-63 70.6 70.6-31 31c-4.5 4.5-10.6 7-17 7H40c-13.3 0-24-10.7-24-24v-4.7c0-6.4 2.5-12.5 7-17z" />
    </svg>
  )
}

export const LinkButtonGroup = ({
  editor,
  popupDelay,
}: {
  editor: Editor | null
  popupDelay: number
}) => {
  if (!editor) {
    return null
  }
  const [showModal, setShowModal] = useState(false)

  let url = editor.getAttributes('link').href
  let title = ''
  if (url) {
    const head = editor.state.selection.head
    title = editor.$pos(head).textContent
  }

  const linkButton = (
    <Button
      icon="linkify"
      onClick={() => setShowModal(true)}
      active={editor.isActive('link')}
    />
  )
  const unlinkButton = (
    <Button
      icon="unlinkify"
      onClick={() => editor.chain().focus().unsetLink().run()}
      disabled={!editor.isActive('link')}
    />
  )

  const ref = useRef(null)
  useEffect(() => {
    if (showModal) {
      ref.current.focus()
    }
  }, [showModal])

  function handleSubmit(e) {
    if (url) {
      if (!url.startsWith('http://') && !url.startsWith('https://')) {
        url = 'https://' + url
      }
      editor
        .chain()
        .focus()
        .extendMarkRange('link')
        .setLink({ href: url })
        .command(({ tr }) => {
          if (title) {
            tr.insertText(title)
          }
          return true
        })
        .run()
    }
    setShowModal(false)
  }

  return (
    <>
      <Button.Group basic style={{ marginRight: '0.5rem' }}>
        <Popup
          content="Add link"
          mouseEnterDelay={popupDelay}
          trigger={linkButton}
        />
        <Popup
          content="Remove link"
          mouseEnterDelay={popupDelay}
          trigger={unlinkButton}
        />
      </Button.Group>
      <Modal
        as="Form"
        className="form"
        open={showModal}
        onClose={() => setShowModal(false)}
        onSubmit={(e) => handleSubmit(e)}
        size="tiny"
      >
        <Modal.Header>Add a link</Modal.Header>
        <Modal.Content>
          <Form.Field required>
            <label>URL</label>
            <Input
              name="url"
              defaultValue={url}
              onChange={(e) => {
                e.preventDefault()
                url = e.target.value
              }}
              ref={ref}
              placeholder="https://"
            />
          </Form.Field>
          <Form.Field>
            <label>Title</label>
            <Input
              name="title"
              defaultValue={title}
              onChange={(e) => {
                e.preventDefault()
                title = e.target.value
              }}
            />
          </Form.Field>
        </Modal.Content>
        <Modal.Actions>
          <Button type="button" onClick={() => setShowModal(false)}>
            Cancel
          </Button>
          <Button primary type="submit">
            Add link
          </Button>
        </Modal.Actions>
      </Modal>
    </>
  )
}

const MenuBar = ({ editor }: { editor: Editor | null }) => {
  if (!editor) {
    return null
  }

  const popupDelay: number = 1000
  const undoButton = (
    <Button
      icon="undo"
      onClick={() => editor.chain().focus().undo().run()}
      disabled={!editor.can().chain().focus().undo().run()}
    />
  )
  const redoButton = (
    <Button
      icon="redo"
      onClick={() => editor.chain().focus().redo().run()}
      disabled={!editor.can().chain().focus().redo().run()}
    />
  )
  const boldButton = (
    <Button
      icon="bold"
      onClick={() => editor.chain().focus().toggleBold().run()}
      active={editor.isActive('bold')}
    />
  )
  const italicButton = (
    <Button
      icon="italic"
      onClick={() => editor.chain().focus().toggleItalic().run()}
      disabled={!editor.can().chain().focus().toggleItalic().run()}
      active={editor.isActive('italic')}
    />
  )
  const underlineButton = (
    <Button
      icon="underline"
      onClick={() => editor.chain().focus().toggleUnderline().run()}
      disabled={!editor.can().chain().focus().toggleUnderline().run()}
      active={editor.isActive('underline')}
    />
  )
  const strikeButton = (
    <Button
      icon="strikethrough"
      onClick={() => editor.chain().focus().toggleStrike().run()}
      disabled={!editor.can().chain().focus().toggleStrike().run()}
      active={editor.isActive('strike')}
    />
  )
  const highlightButton = (
    <Button
      icon
      onClick={() => editor.chain().focus().toggleHighlight().run()}
      disabled={!editor.can().chain().focus().toggleHighlight().run()}
      active={editor.isActive('highlight')}
    >
      <IconHighlighter height={'12px'} />
    </Button>
  )

  return (
    <Segment size="mini">
      <Button.Group basic style={{ marginRight: '0.5rem' }}>
        <Popup
          content="Bold"
          mouseEnterDelay={popupDelay}
          trigger={boldButton}
        />
        <Popup
          content="Italic"
          mouseEnterDelay={popupDelay}
          trigger={italicButton}
        />
        <Popup
          content="Strikethrough"
          mouseEnterDelay={popupDelay}
          trigger={strikeButton}
        />
        <Popup
          content="Underline"
          mouseEnterDelay={popupDelay}
          trigger={underlineButton}
        />
        <Popup
          content="Highlight text"
          mouseEnterDelay={popupDelay}
          trigger={highlightButton}
        />
      </Button.Group>
      <Button.Group basic style={{ marginRight: '0.5rem' }}>
        <Button icon="align left" />
        <Button icon="align center" />
        <Button icon="align right" />
        <Button icon="align justify" />
      </Button.Group>{' '}
      <LinkButtonGroup editor={editor} popupDelay={popupDelay} />{' '}
      <Button.Group basic style={{ marginRight: '0.5rem' }}>
        <Popup
          content="Undo"
          mouseEnterDelay={popupDelay}
          trigger={undoButton}
        />
        <Popup
          content="Redo"
          mouseEnterDelay={popupDelay}
          trigger={redoButton}
        />
      </Button.Group>{' '}
    </Segment>
  )
}

const extensions = [
  TextStyle,
  Underline,
  Highlight,
  StarterKit.configure({
    bulletList: {
      keepMarks: true,
      // TODO : Making this as `false` because marks are not preserved when I try to
      // preserve attrs, awaiting a bit of help
      keepAttributes: false,
    },
    orderedList: {
      keepMarks: true,
      // TODO : Making this as `false` because marks are not preserved when I try to
      // preserve attrs, awaiting a bit of help
      keepAttributes: false,
    },
  }),
  Placeholder.configure({
    placeholder: 'Leave a comment…',
  }),
  Link.configure({
    openOnClick: false,
  }),
]

export interface RichtextEditorProps {
  onSubmit: (editor: Editor) => void
}

export const RichtextEditor = ({ onSubmit }: RichtextEditorProps) => {
  const editor: Editor = useEditor({
    extensions: extensions,
  })
  return (
    <Segment.Group>
      <MenuBar editor={editor} />
      <Segment
        className="ProseMirror-parent"
        style={{ padding: '0.5rem', height: 'auto' }}
      >
        <EditorContent editor={editor} />
        <div style={{ padding: '0' }}>
          <Popup
            content="Submit comment"
            mouseEnterDelay={1000}
            trigger={
              <Button
                circular
                icon="arrow up"
                size="small"
                style={{
                  display: 'block',
                  marginLeft: 'auto',
                  marginRight: '0',
                }}
                onClick={() => onSubmit(editor)}
              />
            }
          />
        </div>
      </Segment>
    </Segment.Group>
  )
}

export const RichtextDisplay = ({ content }: { content: JSONContent }) => {
  const editor: Editor = useEditor({
    editable: false,
    content: content,
    extensions: extensions,
  })
  return <EditorContent className="ProseMirror-display" editor={editor} />
}
