import React, { useState, useRef, useEffect } from 'react'
import TextStyle from '@tiptap/extension-text-style'
import Placeholder from '@tiptap/extension-placeholder'
import Underline from '@tiptap/extension-underline'
import Link from '@tiptap/extension-link'
import Highlight from '@tiptap/extension-highlight'
import { useEditor, EditorContent, Editor, EditorEvents } from '@tiptap/react'
import StarterKit from '@tiptap/starter-kit'
import TextAlign from '@tiptap/extension-text-align'
import { Level } from '@tiptap/extension-heading'
import { EditorState } from 'prosemirror-state'
import {
  Button,
  Segment,
  Popup,
  Modal,
  Form,
  Input,
  Icon,
  SemanticSIZES,
  Label,
} from 'semantic-ui-react'

export type { Editor, EditorEvents }
export { useEditor, Placeholder }

export const resetEditor = (editor: Editor) => {
  if (editor) {
    /* Clear editor content & history. Be nice to have a cleaner way to
     * clear history. See https://github.com/ueberdosis/tiptap/issues/491
     */
    editor.commands.clearContent()
    editor.view.updateState(
      EditorState.create({
        doc: editor.state.doc,
        plugins: editor.state.plugins,
        schema: editor.state.schema,
      })
    )
  }
}
// icon:highlighter | Fontawesome https://fontawesome.com/ | Fontawesome
function IconHighlighter(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg
      viewBox="0 0 576 512"
      fill="currentColor"
      height="1em"
      width="1em"
      {...props}
    >
      <path d="M331 315l158.4-215-29.3-29.4L245 229l86 86zm-187 5v-71.7c0-15.3 7.2-29.6 19.5-38.6L436.6 8.4C444 2.9 453 0 462.2 0c11.4 0 22.4 4.5 30.5 12.6l54.8 54.8c8.1 8.1 12.6 19 12.6 30.5 0 9.2-2.9 18.2-8.4 25.6l-201.3 273c-9 12.3-23.4 19.5-38.6 19.5H240l-25.4 25.4c-12.5 12.5-32.8 12.5-45.3 0l-50.7-50.7c-12.5-12.5-12.5-32.8 0-45.3L144 320zM23 466.3l63-63 70.6 70.6-31 31c-4.5 4.5-10.6 7-17 7H40c-13.3 0-24-10.7-24-24v-4.7c0-6.4 2.5-12.5 7-17z" />
    </svg>
  )
}

// icon:368-clear-formatting | Icomoon https://icomoon.io/ | Keyamoon
function Icon368ClearFormatting(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg
      viewBox="0 0 16 16"
      fill="currentColor"
      height="1em"
      width="1em"
      {...props}
    >
      <path
        fill="currentColor"
        d="M0 14h9v2H0zM14 2H9.273L6.402 13H4.335L7.206 2H3.001V0h11zm.528 14L12.5 13.972 10.472 16l-.972-.972L11.528 13 9.5 10.972l.972-.972 2.028 2.028L14.528 10l.972.972L13.472 13l2.028 2.028z"
      />
    </svg>
  )
}

const LinkButtonGroup = ({
  editor,
  popupDelay,
  buttonSize = 'mini',
}: {
  editor: Editor | null
  popupDelay: number
  buttonSize?: SemanticSIZES
}) => {
  if (!editor) {
    return null
  }
  const [showModal, setShowModal] = useState(false)

  let url = editor.getAttributes('link').href
  let title = ''
  if (url) {
    // Try to get the link text.
    const head = editor.state.selection.head
    title = editor.$pos(head).textContent
  }

  const ref = useRef(null)
  useEffect(() => {
    if (showModal) {
      ref.current.focus()
    }
  }, [showModal])

  function handleSubmit(e) {
    e.stopPropagation()
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
      <Button.Group basic size={buttonSize}>
        <Popup
          content="Add link"
          mouseEnterDelay={popupDelay}
          trigger={
            <Button
              type="button"
              icon="linkify"
              onMouseDown={(e) => e.preventDefault()}
              onClick={() => setShowModal(true)}
              active={editor.isActive('link')}
            />
          }
        />
        <Popup
          content="Remove link"
          mouseEnterDelay={popupDelay}
          trigger={
            <Button
              type="button"
              icon="unlinkify"
              onMouseDown={(e) => e.preventDefault()}
              onClick={() => editor.chain().focus().unsetLink().run()}
              disabled={!editor.isActive('link')}
            />
          }
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

const RichTextEditorToolBar = ({
  editor,
  popupDelay,
  buttonSize = 'mini',
}: {
  editor: Editor | null
  popupDelay: number
  buttonSize?: SemanticSIZES
}) => {
  if (!editor) {
    return null
  }

  const headingLevels: Level[] = [1, 2, 3, 4]

  return (
    <Segment className="toolbar" size="mini">
      <Button.Group basic size={buttonSize}>
        <Popup
          content="Bold"
          mouseEnterDelay={popupDelay}
          trigger={
            <Button
              type="button"
              icon="bold"
              onMouseDown={(e) => e.preventDefault()}
              onClick={(e) => editor.chain().focus().toggleBold().run()}
              active={editor.isActive('bold')}
            />
          }
        />
        <Popup
          content="Italic"
          mouseEnterDelay={popupDelay}
          trigger={
            <Button
              type="button"
              icon="italic"
              onMouseDown={(e) => e.preventDefault()}
              onClick={(e) => editor.chain().focus().toggleItalic().run()}
              disabled={!editor.can().chain().focus().toggleItalic().run()}
              active={editor.isActive('italic')}
            />
          }
        />
        <Popup
          content="Strikethrough"
          mouseEnterDelay={popupDelay}
          trigger={
            <Button
              type="button"
              icon="strikethrough"
              onMouseDown={(e) => e.preventDefault()}
              onClick={(e) => editor.chain().focus().toggleStrike().run()}
              disabled={!editor.can().chain().focus().toggleStrike().run()}
              active={editor.isActive('strike')}
            />
          }
        />
        <Popup
          content="Underline"
          mouseEnterDelay={popupDelay}
          trigger={
            <Button
              type="button"
              icon="underline"
              onMouseDown={(e) => e.preventDefault()}
              onClick={(e) => editor.chain().focus().toggleUnderline().run()}
              disabled={!editor.can().chain().focus().toggleUnderline().run()}
              active={editor.isActive('underline')}
            />
          }
        />
        <Popup
          content="Highlight text"
          mouseEnterDelay={popupDelay}
          trigger={
            <Button
              type="button"
              icon
              onMouseDown={(e) => e.preventDefault()}
              onClick={(e) => editor.chain().focus().toggleHighlight().run()}
              disabled={!editor.can().chain().focus().toggleHighlight().run()}
              active={editor.isActive('highlight')}
            >
              <IconHighlighter />
            </Button>
          }
        />
        <Popup
          content="Clear formatting"
          mouseEnterDelay={popupDelay}
          trigger={
            <Button
              icon
              type="button"
              onMouseDown={(e) => e.preventDefault()}
              onClick={(e) => editor.chain().focus().unsetAllMarks().run()}
            >
              <Icon368ClearFormatting />
            </Button>
          }
        />
      </Button.Group>
      <Button.Group basic size={buttonSize}>
        {Array.from(headingLevels, (level: Level) => {
          return (
            <Popup
              key={level}
              content={'Heading ' + level}
              mouseEnterDelay={popupDelay}
              trigger={
                <Button
                  type="button"
                  icon
                  onMouseDown={(e) => e.preventDefault()}
                  onClick={(e) =>
                    editor.chain().focus().toggleHeading({ level: level }).run()
                  }
                  active={editor.isActive('heading', { level: level })}
                >
                  <Icon name="header">{level}</Icon>
                </Button>
              }
            />
          )
        })}
      </Button.Group>
      <Button.Group basic size={buttonSize}>
        <Popup
          content="Quote"
          mouseEnterDelay={popupDelay}
          trigger={
            <Button
              type="button"
              icon="quote right"
              onMouseDown={(e) => e.preventDefault()}
              onClick={(e) => editor.chain().focus().toggleBlockquote().run()}
              active={editor.isActive('blockquote')}
            />
          }
        />
        <Popup
          content="Bullet list"
          mouseEnterDelay={popupDelay}
          trigger={
            <Button
              type="button"
              icon="list ul"
              onMouseDown={(e) => e.preventDefault()}
              onClick={(e) => editor.chain().focus().toggleBulletList().run()}
              active={editor.isActive('bulletList')}
            />
          }
        />
        <Popup
          content="Ordered list"
          mouseEnterDelay={popupDelay}
          trigger={
            <Button
              type="button"
              icon="list ol"
              onMouseDown={(e) => e.preventDefault()}
              onClick={(e) => editor.chain().focus().toggleOrderedList().run()}
              active={editor.isActive('orderedList')}
            />
          }
        />
      </Button.Group>
      <Button.Group basic size={buttonSize}>
        <Popup
          content="Align left"
          mouseEnterDelay={popupDelay}
          trigger={
            <Button
              type="button"
              icon="align left"
              onMouseDown={(e) => e.preventDefault()}
              onClick={() => editor.chain().focus().setTextAlign('left').run()}
              active={editor.isActive({ textAlign: 'left' })}
            />
          }
        />
        <Popup
          content="Align center"
          mouseEnterDelay={popupDelay}
          trigger={
            <Button
              type="button"
              icon="align center"
              onMouseDown={(e) => e.preventDefault()}
              onClick={() =>
                editor.chain().focus().setTextAlign('center').run()
              }
              active={editor.isActive({ textAlign: 'center' })}
            />
          }
        />
        <Popup
          content="Align right"
          mouseEnterDelay={popupDelay}
          trigger={
            <Button
              type="button"
              icon="align right"
              onMouseDown={(e) => e.preventDefault()}
              onClick={() => editor.chain().focus().setTextAlign('right').run()}
              active={editor.isActive({ textAlign: 'right' })}
            />
          }
        />
        <Popup
          content="Justify text"
          mouseEnterDelay={popupDelay}
          trigger={
            <Button
              type="button"
              icon="align justify"
              onMouseDown={(e) => e.preventDefault()}
              onClick={() =>
                editor.chain().focus().setTextAlign('justify').run()
              }
              active={editor.isActive({ textAlign: 'justify' })}
            />
          }
        />
      </Button.Group>
      <LinkButtonGroup
        editor={editor}
        popupDelay={popupDelay}
        buttonSize={buttonSize}
      />
      <Button.Group basic size={buttonSize}>
        <Popup
          content="Undo"
          mouseEnterDelay={popupDelay}
          trigger={
            <Button
              type="button"
              icon="undo"
              onMouseDown={(e) => e.preventDefault()}
              onClick={() => editor.chain().focus().undo().run()}
              disabled={!editor.can().chain().focus().undo().run()}
            />
          }
        />
        <Popup
          content="Redo"
          mouseEnterDelay={popupDelay}
          trigger={
            <Button
              type="button"
              icon="redo"
              onMouseDown={(e) => e.preventDefault()}
              onClick={() => editor.chain().focus().redo().run()}
              disabled={!editor.can().chain().focus().redo().run()}
            />
          }
        />
      </Button.Group>{' '}
    </Segment>
  )
}

const RichTextCommentEditorActions = ({
  editor,
  popupDelay,
  onSubmit,
}: {
  editor: Editor | null
  popupDelay: number
  onSubmit: (editor: Editor) => void
}) => {
  if (!editor) {
    return null
  }

  editor.setOptions({
    editorProps: {
      handleDOMEvents: {
        keydown: (view, e) => {
          if (e.key === 'Enter' && e.ctrlKey) {
            e.preventDefault()
            onSubmit(editor)
          }
        },
      },
    },
  })

  return (
    <div className="actions">
      <Popup
        mouseEnterDelay={popupDelay}
        trigger={
          <Button
            circular
            icon="arrow up"
            size="tiny"
            type="button"
            onClick={() => onSubmit(editor)}
          />
        }
      >
        <p>Submit comment</p>
        <Label>Ctrl</Label>+<Label>Enter</Label>
      </Popup>
    </div>
  )
}

const updatePlaceholder = (editor: Editor, placeholder: string) => {
  if (editor) {
    const extension = editor.extensionManager.extensions.find(
      (extension) => extension.name === 'placeholder'
    )
    if (extension) {
      extension.options.placeholder = placeholder
      // NOOP to update editor
      editor.view.dispatch(editor.state.tr)
    }
  }
}

const updateEditable = (editor: Editor, editable: boolean) => {
  if (editor) {
    editor.setEditable(editable)
  }
}

const updateContent = (editor: Editor, content: string) => {
  if (editor) {
    editor.commands.setContent(content)
  }
}

const updateOnUpdate = (
  editor: Editor,
  handleUpdate: ({}: EditorEvents['update']) => void
) => {
  if (editor) {
    if (handleUpdate) {
      editor.on('update', handleUpdate)
    } else {
      editor.off('update')
    }
  }
}

const updateOnBlur = (
  editor: Editor,
  handleBlur: ({}: EditorEvents['blur']) => void
) => {
  if (editor) {
    if (handleBlur) {
      editor.on('blur', handleBlur)
    } else {
      editor.off('blur')
    }
  }
}

export const EditorExtensions = [
  Highlight,
  Link.configure({
    openOnClick: false,
  }),
  StarterKit,
  TextAlign.configure({
    types: ['heading', 'paragraph'],
  }),
  TextStyle,
  Underline,
]

export interface RichTextCommentProps {
  disabled?: boolean
  onSubmit?: (editor: Editor) => void
  placeholder?: string
  popupDelay?: number
  editor?: Editor
}

export const RichTextCommentEditor = ({
  disabled = false,
  onSubmit,
  placeholder = '',
  popupDelay = 1000,
  editor = useEditor({
    editable: !disabled,
    extensions: [
      ...EditorExtensions,
      Placeholder.configure({ placeholder: placeholder }),
    ],
  }),
}: RichTextCommentProps) => {
  useEffect(() => updatePlaceholder(editor, placeholder), [editor, placeholder])
  useEffect(() => updateEditable(editor, !disabled), [editor, disabled])

  return (
    <Segment.Group className="richtext-editor">
      <Segment className="editor-content">
        <EditorContent className="content" editor={editor} />
        {onSubmit && (
          <RichTextCommentEditorActions
            editor={editor}
            popupDelay={popupDelay}
            onSubmit={onSubmit}
          />
        )}
      </Segment>
    </Segment.Group>
  )
}

export interface RichTextEditorProps {
  content?: string
  disabled?: boolean
  onUpdate?: ({ editor, transaction }: EditorEvents['update']) => void
  onBlur?: ({ editor, event, transaction }: EditorEvents['blur']) => void
  placeholder?: string
  popupDelay?: number
  showToolbar?: boolean
}

export const RichTextEditor = ({
  content,
  disabled = false,
  onBlur,
  onUpdate,
  placeholder = '',
  popupDelay = 1000,
  showToolbar = true,
}: RichTextEditorProps) => {
  const editor: Editor = useEditor({
    content: content,
    editable: !disabled,
    extensions: [
      ...EditorExtensions,
      Placeholder.configure({ placeholder: placeholder }),
    ],
  })
  useEffect(() => updatePlaceholder(editor, placeholder), [editor, placeholder])
  useEffect(() => updateEditable(editor, !disabled), [editor, disabled])
  useEffect(() => updateContent(editor, content), [editor, content])
  useEffect(() => updateOnUpdate(editor, onUpdate), [editor, onUpdate])
  useEffect(() => updateOnBlur(editor, onBlur), [editor, onBlur])

  return (
    <Segment.Group className="richtext-editor">
      {showToolbar && (
        <RichTextEditorToolBar editor={editor} popupDelay={popupDelay} />
      )}
      <Segment className="editor-content">
        <EditorContent className="content" editor={editor} />
      </Segment>
    </Segment.Group>
  )
}

export const RichTextDisplay = ({ content }: { content: string }) => {
  const editor: Editor = useEditor({
    editable: false,
    content: content,
    extensions: EditorExtensions,
  })
  return <EditorContent className="richtext-display" editor={editor} />
}