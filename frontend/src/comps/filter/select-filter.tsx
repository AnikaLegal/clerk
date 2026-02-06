import { Loader, Select, SelectProps } from '@mantine/core'
import React from 'react'

interface SelectFilterProps extends SelectProps {
  name: string
  onFilterChange: (key: string, value: any) => void
  isLoading?: boolean
}

const SelectFilter = ({
  name,
  onFilterChange,
  isLoading = false,
  ...props
}: SelectFilterProps) => {
  return (
    <Select
      clearable
      size="md"
      withCheckIcon={false}
      onChange={(value) => onFilterChange(name, value)}
      rightSection={isLoading ? <Loader size="sm" /> : null}
      {...props}
    />
  )
}

export default SelectFilter
