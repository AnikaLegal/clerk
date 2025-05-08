import {
  ComboboxData,
  ComboboxItem,
  ComboboxLikeRenderOptionInput,
  Loader,
  Select,
} from '@mantine/core'
import { useDebouncedCallback } from '@mantine/hooks'
import { IconSearch } from '@tabler/icons-react'
import React from 'react'

import '@mantine/core/styles.css'

export interface SelectSearchProps {
  data?: ComboboxData | undefined
  loading?: boolean | undefined
  placeholder?: string | undefined
  nothingFoundMessage?: string
  onSearchChange: (value: string) => void
  onChange?: (value: string | null, option: ComboboxItem) => void
  searchDelay?: number | undefined
  renderOption?:
    | ((item: ComboboxLikeRenderOptionInput<ComboboxItem>) => React.ReactNode)
    | undefined
}

export const SelectSearch = ({
  data,
  loading,
  placeholder = 'Search...',
  nothingFoundMessage = 'Nothing found...',
  searchDelay = 300,
  onChange,
  onSearchChange,
  renderOption,
}: SelectSearchProps) => {
  const delayedOnSearchChange = useDebouncedCallback(
    onSearchChange,
    searchDelay
  )
  return (
    <Select
      searchable
      clearable
      size="md"
      styles={{
        input: {
          paddingLeft: 'unset',
          paddingInlineStart: 'var(--input-padding-inline-start)',
        },
      }}
      leftSection={<IconSearch size={20} />}
      placeholder={placeholder}
      data={data}
      filter={({ options }) => options}
      rightSection={loading && <Loader size="sm" />}
      renderOption={renderOption}
      nothingFoundMessage={nothingFoundMessage}
      onSearchChange={delayedOnSearchChange}
      onChange={onChange}
    />
  )
}
