import React from 'react'
import { Box, Center, Container, Text } from '@mantine/core'
import { IconDeviceUnknown } from '@tabler/icons-react'

const NotFound = () => (
  <Container size="xl">
    <Center mih="65vh">
      <Box ta="center">
        <IconDeviceUnknown
          size={100}
          stroke={1.75}
          color="var(--mantine-color-dark-4)"
        />
        <Text size="lg" mt="sm">
          Not Found
        </Text>
        <Text>The page you requested could not be found.</Text>
      </Box>
    </Center>
  </Container>
)

export default NotFound
