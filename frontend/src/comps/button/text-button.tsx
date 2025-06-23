import React from 'react'
import { Button, ElementProps } from '@mantine/core'

import '@mantine/core/styles.css'

export const TextButton = ({ children, ...props }: ElementProps<'button'>) => {
  return (
    <Button
      variant="transparent"
      size="compact-xs"
      fz="lg"
      fw="normal"
      c="blue.6"
      radius="xs"
      {...props}
    >
      {children}
    </Button>
  )
}

export default TextButton
