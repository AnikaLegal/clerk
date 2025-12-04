import React from 'react'
import { Box, Center, Container, Text } from '@mantine/core'
import { IconBan } from '@tabler/icons-react'

const NotAllowed = () => (
  <Container size="xl">
    <Center mih="65vh">
      <Box ta="center">
        {/* Use a color in the range defined by the standard. See
        https://en.wikipedia.org/wiki/No_symbol#Color_red_per_3864-1 */}
        <IconBan size={100} color="#b00000" />
        <Text size="lg" mt="sm">
          Not Allowed
        </Text>
        <Text>You do not have permission to access this page.</Text>
      </Box>
    </Center>
  </Container>
)

export default NotAllowed
