import {
  ActionIcon,
  ActionIconProps,
  Tooltip,
  TooltipProps,
} from '@mantine/core'
import { useDisclosure, UseDisclosureOptions } from '@mantine/hooks'
import React, { useState } from 'react'
import ActionConfirmationButton, {
  ActionConfirmationProps,
} from './action-confirmation-button'

export interface ActionIconWithConfirmationProps {
  actionIcon?: ActionIconProps
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
}

export const ActionIconWithConfirmationGroup = ({
  children,
}: ActionIconWithConfirmationGroupProps) => {
  const [activeIndex, setActiveIndex] = useState<number | null>(null)

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
      return (
        <ActionIcon.Group>
          {React.cloneElement(child, { confirmButton })}
        </ActionIcon.Group>
      )
    }
    return <ActionIcon.Group>{child}</ActionIcon.Group>
  }

  return (
    <ActionIcon.Group>
      {childrenArray.map((child, index) => {
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
      })}
    </ActionIcon.Group>
  )
}

ActionIconWithConfirmation.Group = ActionIconWithConfirmationGroup

export default ActionIconWithConfirmation
