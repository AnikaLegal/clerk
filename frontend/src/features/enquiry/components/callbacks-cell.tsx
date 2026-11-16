import { NumberInput } from '@mantine/core'
import React, { useEffect, useRef, useState } from 'react'
import styles from './inline-edit.module.css'

interface CallbacksCellProps {
  callbacks: number
  onSave: (callbacks: number) => Promise<unknown>
}

// Always an input, styled to read as plain text until hovered or focused.
// Enter or leaving the field saves a change; Esc puts the saved value back.
const CallbacksCell = ({ callbacks, onSave }: CallbacksCellProps) => {
  const [value, setValue] = useState(callbacks)
  const [isSaving, setIsSaving] = useState(false)
  const isCancelling = useRef(false)

  useEffect(() => setValue(callbacks), [callbacks])

  const save = () => {
    if (isCancelling.current) {
      isCancelling.current = false
      return
    }
    if (value === callbacks || isSaving) {
      return
    }
    setIsSaving(true)
    onSave(value)
      .catch(() => setValue(callbacks))
      .finally(() => setIsSaving(false))
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.currentTarget.blur()
    } else if (e.key === 'Escape') {
      isCancelling.current = true
      setValue(callbacks)
      e.currentTarget.blur()
    }
  }

  return (
    <NumberInput
      aria-label="Callbacks"
      classNames={{
        root: styles.numberRoot,
        input: styles.numberInput,
        section: styles.numberSection,
      }}
      size="xs"
      autoComplete="off"
      min={0}
      allowDecimal={false}
      allowNegative={false}
      disabled={isSaving}
      value={value}
      onChange={(next) => setValue(Number(next) || 0)}
      onKeyDown={handleKeyDown}
      onBlur={save}
    />
  )
}

export default CallbacksCell
