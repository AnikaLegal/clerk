import { Group, Text } from '@mantine/core'
import api from 'api'
import { SelectSearchField, SelectSearchFieldProps } from 'forms/formik'
import React, { useState } from 'react'
import { useEffectLazy } from 'utils'

type ClientRecord = Record<
  string,
  { full_name: string; preferred_name: string | null; email: string }
>

export interface ClientSelectSearchFieldProps
  extends Omit<SelectSearchFieldProps, 'onSearchChange'> {
  minQueryLength?: number
}

export const ClientSelectSearchField = ({
  minQueryLength = 3,
  ...props
}: ClientSelectSearchFieldProps) => {
  const [query, setQuery] = useState<string>('')
  const [page, setPage] = useState(1)
  const [isLoading, setIsLoading] = useState(false)
  const [results, setResults] = useState<ClientRecord>({})
  const [getClients] = api.useLazyGetClientsQuery()

  const search = () => {
    if (query.length < minQueryLength) {
      setIsLoading(false)
      return
    }
    setIsLoading(true)
    getClients({ q: query, page: page })
      .unwrap()
      .then((response) => {
        const nextResult: ClientRecord = Object.fromEntries(
          response.results.map((client) => [
            client.id,
            {
              full_name: client.full_name,
              preferred_name: client.preferred_name,
              email: client.email,
            },
          ])
        )
        setResults({ ...results, ...nextResult })

        if (response.next) {
          setPage(response.next)
        } else {
          setIsLoading(false)
        }
      })
      .catch(() => {
        setIsLoading(false)
      })
  }
  useEffectLazy(() => search(), [query, page])

  const handleSearchChange = (value) => {
    if (value != query) {
      setResults({})
      setPage(1)
      setQuery(value)
    }
  }

  const renderOption = ({ option }) => {
    const client = results[option.value]
    return (
      <Group gap="sm">
        <div>
          <Text size="md">
            {client.full_name}{' '}
            {client.preferred_name ? `(${client.preferred_name})` : ''}
          </Text>
          <Text size="sm" opacity={0.5}>
            {client.email}
          </Text>
        </div>
      </Group>
    )
  }

  const nothingFoundMessage =
    query.length == 0
      ? ''
      : query.length < minQueryLength
        ? 'Search value too short'
        : 'Nothing found...'

  const data = Object.entries(results).map(([id, { full_name }]) => {
    return { value: id, label: full_name }
  })

  return (
    <SelectSearchField
      data={data}
      onSearchChange={handleSearchChange}
      renderOption={renderOption}
      loading={isLoading}
      nothingFoundMessage={nothingFoundMessage}
      {...props}
    />
  )
}
