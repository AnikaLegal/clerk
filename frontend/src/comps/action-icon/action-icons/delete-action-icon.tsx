import { IconTrash } from '@tabler/icons-react'
import {
  ActionIconWithConfirmation,
  ActionIconWithConfirmationProps,
} from 'comps/action-icon'
import React from 'react'

const DeleteActionIconWithConfirmation = ({
  onClick,
  confirmButton,
}: {
  onClick: ActionIconWithConfirmationProps['onClick']
  confirmButton: ActionIconWithConfirmationProps['confirmButton']
}) => {
  return (
    <ActionIconWithConfirmation
      tooltip={{ label: 'Delete' }}
      icon={<IconTrash stroke={1.5} />}
      onClick={onClick}
      confirmButton={confirmButton}
    />
  )
}

export default DeleteActionIconWithConfirmation
