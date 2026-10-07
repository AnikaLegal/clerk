import React from 'react'
import { Button, Center, Text } from '@mantine/core'
import { IconCloudOff } from '@tabler/icons-react'
import ErrorMessage, { ErrorScreenProps } from 'comps/error/error-message'

const ServerError = ({ compact }: ErrorScreenProps) => (
  <ErrorMessage
    icon={
      <IconCloudOff
        size={64}
        stroke={1.75}
        color="var(--mantine-color-dark-4)"
      />
    }
    title="Clerk is temporarily unavailable"
    compact={compact}
  >
    <Text>
      This usually clears up within a few minutes. Reload the page in a moment.
      If it's still down after ten minutes, let us know in{' '}
      <Text span fw={700}>
        #tech
      </Text>
      .
    </Text>
    <Center>
      <Button onClick={() => window.location.reload()}>Reload</Button>
    </Center>
  </ErrorMessage>
)

export default ServerError
