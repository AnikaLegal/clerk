import { Group, Loader, Select, SelectProps, Text } from '@mantine/core'
import { Client } from 'api'
import React from 'react'

import '@mantine/core/styles.css'

export type ClientLikeData = Pick<
  Client,
  'id' | 'first_name' | 'last_name' | 'email'
>
export interface ClientSelectInputProps extends Omit<SelectProps, 'data'> {
  data: ClientLikeData[]
  isLoading?: boolean
}

const ClientSelectInput = ({
  data,
  isLoading = false,
  ...props
}: ClientSelectInputProps) => {
  const renderOption = ({ option }) => {
    const client = data.find((client) => client.id === option.value)
    if (!client) {
      return undefined
    }
    return (
      <Group gap="sm">
        <div>
          <Text size="md">
            {client.first_name} {client.last_name}
          </Text>
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
      data={data.map((client) => {
        return {
          value: client.id,
          label: `${client.first_name} ${client.last_name} (${client.email})`,
        }
      })}
      renderOption={renderOption}
      rightSection={isLoading && <Loader size="sm" />}
      nothingFoundMessage="No clients found"
      placeholder="Search for an existing client"
      limit={100}
      {...props}
    />
  )
}

export default ClientSelectInput
