import { Loader, Select, SelectProps } from '@mantine/core'
import { GetUsersApiArg, useGetUsersQuery, User } from 'api'
import React, { useEffect, useState } from 'react'

// UserSelect supplies its own data, fetched with `usersQuery`.
interface UserSelectProps extends Omit<SelectProps, 'data'> {
  usersQuery: GetUsersApiArg
}

export const UserSelect = ({ usersQuery, ...props }: UserSelectProps) => {
  const [data, setData] = useState<User[]>([])
  const [args, setArgs] = useState<GetUsersApiArg>({
    ...usersQuery,
    page: 1,
    pageSize: 100,
  })
  const result = useGetUsersQuery(args)

  useEffect(() => {
    if (result.data) {
      setData((prev) => [...prev, ...result.data!.results])
      // If there are more pages, fetch the next one
      if (result.data.next !== null) {
        setArgs((prev) => ({ ...prev, page: args.page! + 1 }))
      }
    }
  }, [result.data])

  const showLoading = result.isLoading || result.data?.next !== null
  return (
    <Select
      searchable
      clearable
      size="md"
      {...props}
      data={data.map((u) => ({
        value: String(u.id),
        label: u.email,
      }))}
      rightSection={showLoading && <Loader size="sm" />}
    />
  )
}
