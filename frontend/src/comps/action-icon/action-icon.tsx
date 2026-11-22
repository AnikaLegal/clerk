import {
  ActionIcon,
  ActionIconProps,
  Group,
  MantineSpacing,
  Tooltip,
  TooltipProps,
} from '@mantine/core'
import { useDisclosure, UseDisclosureOptions } from '@mantine/hooks'
import React, { useState } from 'react'
import ActionConfirmationButton, {
  ActionConfirmationProps,
} from './action-confirmation-button'

export interface ActionIconWithConfirmationProps {
  actionIcon?: ActionIconProps & { 'aria-label'?: string }
  tooltip: TooltipProps
  icon: React.ReactNode
  onClick: () => void
  confirmButton?: {
    label: ActionConfirmationProps['label']
    color?: ActionConfirmationProps['color']
    options?: UseDisclosureOptions
    closeOnConfirm?: boolean
  }
}
const ActionIconWithConfirmation = ({
  actionIcon,
  tooltip,
  icon,
  onClick,
  confirmButton,
}: ActionIconWithConfirmationProps) => {
  const [opened, handler] = useDisclosure(false, confirmButton?.options)

  if (confirmButton && opened) {
    const handleConfirm = () => {
      onClick()
      if (confirmButton.closeOnConfirm !== false) {
        handler.close()
      }
    }
    return (
      <ActionConfirmationButton
        onConfirm={handleConfirm}
        confirmHandler={handler}
        label={confirmButton.label}
        color={confirmButton.color}
      />
    )
  }
  return (
    <ActionIcon
      variant="transparent"
      color="gray"
      onClick={confirmButton ? handler.open : onClick}
      {...actionIcon}
    >
      <Tooltip openDelay={750} {...tooltip}>
        {icon}
      </Tooltip>
    </ActionIcon>
  )
}

interface ActionIconWithConfirmationGroupProps {
  children: React.ReactNode
  // Spaces the icons apart instead of joining them into one strip.
  gap?: MantineSpacing
}

export const ActionIconWithConfirmationGroup = ({
  children,
  gap,
}: ActionIconWithConfirmationGroupProps) => {
  const [activeIndex, setActiveIndex] = useState<number | null>(null)
  // A confirm button on its own is centred where the icons were.
  const wrap = (content: React.ReactNode, isConfirming = false) =>
    gap === undefined ? (
      <ActionIcon.Group>{content}</ActionIcon.Group>
    ) : (
      <Group
        gap={gap}
        wrap="nowrap"
        justify={isConfirming ? 'center' : undefined}
      >
        {content}
      </Group>
    )

  // Ensure children are ReactElements with the expected props
  const childrenArray = React.Children.toArray(children)
  if (activeIndex !== null) {
    const child = childrenArray[activeIndex]
    if (
      React.isValidElement<ActionIconWithConfirmationProps>(child) &&
      child.props.confirmButton
    ) {
      const options = child.props.confirmButton.options
      const onClose = () => {
        setActiveIndex(null)
        if (options && options.onClose) {
          options.onClose()
        }
      }
      const confirmButton = {
        ...child.props.confirmButton,
        options: { ...options, onClose },
      }
      return wrap(React.cloneElement(child, { confirmButton }), true)
    }
    return wrap(child)
  }

  return wrap(
    childrenArray.map((child, index) => {
      if (
        React.isValidElement<ActionIconWithConfirmationProps>(child) &&
        child.props.confirmButton
      ) {
        const options = child.props.confirmButton.options
        const onOpen = () => {
          setActiveIndex(index)
          if (options && options.onOpen) {
            options.onOpen()
          }
        }
        const confirmButton = {
          ...child.props.confirmButton,
          options: { ...options, onOpen },
        }
        return React.cloneElement(child, { confirmButton })
      }
      return child
    })
  )
}

ActionIconWithConfirmation.Group = ActionIconWithConfirmationGroup

export default ActionIconWithConfirmation
