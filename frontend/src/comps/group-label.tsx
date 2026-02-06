import React from 'react'
import { Badge, Group } from '@mantine/core'

const GROUP_COLORS = {
  Admin: 'red.7',
  Lawyer: 'orange.5',
  Coordinator: 'green.6',
  Paralegal: 'blue',
}

export const GroupLabels = ({ groups, isSuperUser }) => (
  <Group gap="0.25rem">
    {groups.map((groupName) => (
      <Badge
        key={groupName}
        color={GROUP_COLORS[groupName] || 'gray.3'}
        radius="sm"
        size="lg"
        tt="none"
        autoContrast
      >
        {groupName}
      </Badge>
    ))}
    {isSuperUser && (
      <Badge
        key="Superuser"
        color="black"
        radius="sm"
        size="lg"
        tt="none"
        autoContrast
      >
        Superuser 😎
      </Badge>
    )}
  </Group>
)
