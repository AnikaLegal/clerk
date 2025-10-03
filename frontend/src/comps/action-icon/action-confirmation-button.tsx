import { Button, MantineColor } from '@mantine/core'
import {
  UseDisclosureHandlers,
  useClickOutside,
  useDebouncedCallback,
} from '@mantine/hooks'
import React from 'react'

export interface ActionConfirmationProps {
  onConfirm: () => void
  confirmHandler: UseDisclosureHandlers
  label: React.ReactNode
  color?: MantineColor
}
const ActionConfirmationButton = ({
  onConfirm,
  confirmHandler,
  label,
  color,
}: ActionConfirmationProps) => {
  const delayedHideConfirm = useDebouncedCallback(() => {
    confirmHandler.close()
  }, 100)
  const ref = useClickOutside(() => delayedHideConfirm())

  return (
    <div ref={ref}>
      <Button
        variant="filled"
        color={color}
        size="compact-sm"
        onClick={onConfirm}
      >
        {label}
      </Button>
    </div>
  )
}

export default ActionConfirmationButton
