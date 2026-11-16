import { Text, Textarea, UnstyledButton } from '@mantine/core'
import React, { useRef, useState } from 'react'
import styles from './comment-cell.module.css'

interface CommentCellProps {
  comments: string
  onSave: (comments: string) => Promise<unknown>
}

// Click a comment to edit it in place. Enter or leaving the field saves a
// change; Esc throws it away.
const CommentCell = ({ comments, onSave }: CommentCellProps) => {
  const [draft, setDraft] = useState<string | null>(null)
  const [isSaving, setIsSaving] = useState(false)
  // Enter and the blur that follows can both try to finish the edit.
  const isFinishing = useRef(false)

  if (draft === null) {
    return (
      <UnstyledButton
        className={styles.display}
        aria-label={comments ? 'Edit comment' : 'Add comment'}
        onClick={() => {
          isFinishing.current = false
          setDraft(comments)
        }}
      >
        {comments || <span className={styles.placeholder}>Add comment</span>}
      </UnstyledButton>
    )
  }

  const finish = (save: boolean) => {
    if (isFinishing.current) {
      return
    }
    isFinishing.current = true
    if (!save || draft === comments) {
      setDraft(null)
      return
    }
    setIsSaving(true)
    onSave(draft)
      .then(() => setDraft(null))
      .catch(() => {
        isFinishing.current = false
      })
      .finally(() => setIsSaving(false))
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Escape') {
      finish(false)
    } else if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      finish(true)
    }
  }

  return (
    <>
      <Textarea
        aria-label="Comment"
        size="md"
        autoComplete="off"
        autoFocus
        autosize
        minRows={1}
        disabled={isSaving}
        value={draft}
        onChange={(e) => setDraft(e.currentTarget.value)}
        onKeyDown={handleKeyDown}
        onFocus={(e) => {
          const end = e.currentTarget.value.length
          e.currentTarget.setSelectionRange(end, end)
        }}
        onBlur={() => finish(true)}
      />
      <Text c="dimmed" size="xs" mt={4}>
        Enter to save · Shift+Enter for a new line · Esc to cancel
      </Text>
    </>
  )
}

export default CommentCell
