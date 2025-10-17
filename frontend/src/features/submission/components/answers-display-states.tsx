import { Box, Loader } from '@mantine/core'
import React from 'react'

export const EmptyState = () => <Box>No submission data found</Box>

export const LoadingState = () => (
  <Box>
    <Loader />
  </Box>
)
