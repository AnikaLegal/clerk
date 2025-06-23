import { Group, Loader, Select, SelectProps, Text } from '@mantine/core'
import { useGetClientsQuery } from 'api'
import React from 'react'

import '@mantine/core/styles.css'

interface ClientInfo {
  full_name: string
  email: string
}

const ClientSelectInput = (props: SelectProps) => {
  const result = useGetClientsQuery({ pageSize: -1 }) // returns all results.
  const data = result.data?.results || []
  const lookup = data.reduce((acc, obj) => {
    acc.set(obj.id, { full_name: obj.full_name, email: obj.email })
    return acc
  }, new Map<string, ClientInfo>())

  const renderOption = ({ option }) => {
    const client = lookup.get(option.value)
    if (!client) {
      return undefined
    }
    return (
      <Group gap="sm">
        <div>
          <Text size="md">{client.full_name}</Text>
          <Text size="sm" opacity={0.5}>
            {client.email}
          </Text>
        </div>
      </Group>
    )
  }

  return (
    <Select
      clearable
      searchable
      data={Array.from(lookup, ([id, client]) => ({
        value: id,
        label: `${client.full_name} (${client.email})`,
      }))}
      renderOption={renderOption}
      rightSection={result.isFetching && <Loader size="sm" />}
      nothingFoundMessage="No clients found"
      placeholder="Search for an existing client"
      limit={100}
      {...props}
    />
  )
}

export default ClientSelectInput
