import { Center, Popover, PopoverProps, Text } from '@mantine/core'
import { IconInfoCircle } from '@tabler/icons-react'
import React from 'react'

import '@mantine/core/styles.css'

const MarkdownInfoIconWithPopover = (props: PopoverProps) => (
  <Popover {...props}>
    <Popover.Target>
      <Center>
        <IconInfoCircle
          color="var(--mantine-color-dimmed)"
          size={18}
          style={{ cursor: 'pointer' }}
        />
      </Center>
    </Popover.Target>
    <Popover.Dropdown>
      <Text size="sm">
        Text can be formatted using Markdown. See{' '}
        <a
          href="https://www.markdownguide.org/cheat-sheet/#basic-syntax"
          target="_blank"
          rel="noopener noreferrer"
        >
          here
        </a>{' '}
        for a basic reference.
      </Text>
    </Popover.Dropdown>
  </Popover>
)

export default MarkdownInfoIconWithPopover
