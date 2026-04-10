import { Loader, TextInput, TextInputProps } from '@mantine/core'
import { useDebouncedCallback } from '@mantine/hooks'
import { IconSearch } from '@tabler/icons-react'
import React from 'react'

interface TextInputFilterProps extends TextInputProps {
  name: string
  onFilterChange: (key: string, value: any) => void
  isLoading?: boolean
  debounceDelay?: number
}

const TextInputFilter = ({
  name,
  onFilterChange,
  isLoading = false,
  debounceDelay = 300,
  ...props
}: TextInputFilterProps) => {
  const debouncedFilterChange = useDebouncedCallback((key, value) => {
    onFilterChange(key, value)
  }, debounceDelay)

  return (
    <TextInput
      size="md"
      onChange={(event) =>
        debouncedFilterChange(name, event.currentTarget.value)
      }
      rightSection={isLoading ? <Loader size="sm" /> : <IconSearch size={16} />}
      {...props}
    />
  )
}

export default TextInputFilter
