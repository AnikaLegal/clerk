import { IconPencil } from '@tabler/icons-react'
import {
  ActionIconWithConfirmation,
  ActionIconWithConfirmationProps,
} from 'comps/action-icon'
import React from 'react'

interface UpdateActionIconProps
  extends Omit<
    ActionIconWithConfirmationProps,
    'confirmButton' | 'tooltip' | 'icon'
  > {
  tooltip?: ActionIconWithConfirmationProps['tooltip']
}

const UpdateActionIcon = ({ onClick, ...props }: UpdateActionIconProps) => {
  return (
    <ActionIconWithConfirmation
      tooltip={{ label: 'Update' }}
      icon={<IconPencil stroke={1.5} />}
      onClick={onClick}
      {...props}
    />
  )
}

export default UpdateActionIcon
