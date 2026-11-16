import { Text, Textarea, UnstyledButton } from '@mantine/core'
import React from 'react'
import styles from './inline-edit.module.css'
import useInlineEdit from './use-inline-edit'

interface CommentCellProps {
  comments: string
  onSave: (comments: string) => Promise<unknown>
}

const CommentCell = ({ comments, onSave }: CommentCellProps) => {
  const edit = useInlineEdit(comments, onSave)

  if (edit.draft === null) {
    return (
      <UnstyledButton
        className={styles.display}
        aria-label={comments ? 'Edit comment' : 'Add comment'}
        onClick={edit.start}
      >
        {comments || <span className={styles.placeholder}>Add comment</span>}
      </UnstyledButton>
    )
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
        disabled={edit.isSaving}
        value={edit.draft}
        onChange={(e) => edit.setDraft(e.currentTarget.value)}
        onKeyDown={edit.handleKeyDown}
        onFocus={(e) => {
          const end = e.currentTarget.value.length
          e.currentTarget.setSelectionRange(end, end)
        }}
        onBlur={() => edit.finish(true)}
      />
      <Text c="dimmed" size="xs" mt={4}>
        Enter to save · Shift+Enter for a new line · Esc to cancel
      </Text>
    </>
  )
}

export default CommentCell
