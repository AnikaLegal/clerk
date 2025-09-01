import { IconPencil } from '@tabler/icons-react'
import { ActionIconWithConfirmation } from 'comps/action-icon'
import React from 'react'

const UpdateActionIcon = ({ onClick }: { onClick: () => void }) => {
  return (
    <ActionIconWithConfirmation
      tooltip={{ label: 'Update' }}
      icon={<IconPencil stroke={1.5} />}
      onClick={onClick}
    />
  )
}

export default UpdateActionIcon
