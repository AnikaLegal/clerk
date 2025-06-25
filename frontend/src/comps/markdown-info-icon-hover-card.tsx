import { Anchor, HoverCard, HoverCardProps, Text } from '@mantine/core'
import { IconInfoCircle } from '@tabler/icons-react'
import React from 'react'

import '@mantine/core/styles.css'

const MarkdownInfoIconHoverCard = (props: HoverCardProps) => (
  <HoverCard {...props}>
    <HoverCard.Target>
      <IconInfoCircle
        color="var(--mantine-color-dimmed)"
        size={18}
        style={{ cursor: 'pointer' }}
      />
    </HoverCard.Target>
    <HoverCard.Dropdown>
      <Text size="sm">Text can be formatted using Markdown.</Text>
      <Text size="sm">
        See{' '}
        <Anchor
          href="https://www.markdownguide.org/cheat-sheet/#basic-syntax"
          target="_blank"
          rel="noopener noreferrer"
        >
          here
        </Anchor>{' '}
        for a basic reference.
      </Text>
    </HoverCard.Dropdown>
  </HoverCard>
)

export default MarkdownInfoIconHoverCard
