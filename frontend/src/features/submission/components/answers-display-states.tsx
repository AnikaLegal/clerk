import { Box, Group, Loader, Text } from '@mantine/core'
import { IconExclamationCircle } from '@tabler/icons-react'
import { enqueueSnackbar } from 'notistack'
import React, { useEffect } from 'react'
import { getAPIErrorMessage } from 'utils'

export const ErrorState = ({ error }: { error: any }) => {
  useEffect(() => {
    const message = getAPIErrorMessage(error, 'Could not load critical dates')
    enqueueSnackbar(message, { variant: 'error' })
  }, [error])

  return (
    <Box>
      <Group justify="center" gap="xs" m="sm" c="red">
        <IconExclamationCircle />
        <Text>Could not load submission data</Text>
      </Group>
    </Box>
  )
}

export const EmptyState = () => <Box>No submission data found</Box>

export const LoadingState = () => (
  <Box>
    <Loader />
  </Box>
)
