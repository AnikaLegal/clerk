import { Button, darken } from '@mantine/core'
import { NotificationData, notifications } from '@mantine/notifications'
import {
  IconAlertTriangleFilled,
  IconCircleCheckFilled,
  IconCircleXFilled,
  IconInfoCircleFilled,
} from '@tabler/icons-react'
import React from 'react'
import classes from './notification.module.css'

type NotificationType = 'info' | 'success' | 'warning' | 'error'

interface ShowNotificationOptions extends NotificationData {
  type?: NotificationType
  link?: {
    text: string
    url: string
  }
}

export const showNotification = ({
  type = 'info',
  ...props
}: ShowNotificationOptions) => {
  const color = getNotificationColor(type)
  const buttonColor = darken(color, 0.1)
  const icon = getNotificationIcon(type)

  const message = props.link ? (
    <div>
      <div>{props.message}</div>
      <Button
        variant="filled"
        color={buttonColor}
        component="a"
        href={props.link.url}
        target="_blank"
        rel="noopener noreferrer"
        size="compact-sm"
        mt="0.25rem"
      >
        {props.link.text}
      </Button>
    </div>
  ) : (
    props.message
  )

  notifications.show({
    position: 'bottom-left',
    icon: icon,
    ...props,
    message: message,
    color: color,
    classNames: classes,
  })
}

const getNotificationColor = (type: NotificationType) => {
  switch (type) {
    case 'success':
      return '#43a047'
    case 'warning':
      return '#ff9800'
    case 'error':
      return '#d32f2f'
    case 'info':
    default:
      return '#2196f3'
  }
}

const getNotificationIcon = (type: NotificationType) => {
  switch (type) {
    case 'success':
      return <IconCircleCheckFilled />
    case 'warning':
      return <IconAlertTriangleFilled />
    case 'error':
      return <IconCircleXFilled />
    case 'info':
    default:
      return <IconInfoCircleFilled />
  }
}
