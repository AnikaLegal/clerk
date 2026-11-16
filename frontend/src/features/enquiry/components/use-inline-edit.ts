import { useRef, useState } from 'react'

// Click-to-edit state for a table cell. Enter or leaving the field saves a
// change; Esc throws it away.
const useInlineEdit = <V>(value: V, onSave: (value: V) => Promise<unknown>) => {
  const [draft, setDraft] = useState<V | null>(null)
  const [isSaving, setIsSaving] = useState(false)
  // Enter and the blur that follows can both try to finish the edit.
  const isFinishing = useRef(false)

  const start = () => {
    isFinishing.current = false
    setDraft(value)
  }

  const finish = (save: boolean) => {
    if (draft === null || isFinishing.current) {
      return
    }
    isFinishing.current = true
    if (!save || draft === value) {
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

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      finish(false)
    } else if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      finish(true)
    }
  }

  return { draft, setDraft, isSaving, start, finish, handleKeyDown }
}

export default useInlineEdit
