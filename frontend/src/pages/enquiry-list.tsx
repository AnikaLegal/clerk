import {
  Box,
  Container,
  Group,
  Paper,
  SimpleGrid,
  Text,
  ThemeIcon,
  Title,
} from '@mantine/core'
import { IconMail, IconPhone } from '@tabler/icons-react'
import api from 'api'
import {
  CallTable,
  ContactTable,
  EnquiryKind,
  TopicOption,
} from 'features/enquiry'
import React, { useState } from 'react'
import { mount } from 'utils'

interface DjangoContext {
  topic_options: TopicOption[]
}
const CONTEXT = (window as unknown as { REACT_CONTEXT: DjangoContext })
  .REACT_CONTEXT

const App = () => {
  const [kind, setKind] = useState<EnquiryKind>('call')
  // Page size 1: only the totals are needed for the cards.
  const pendingCalls = api.useGetCallsQuery({
    requiresCallback: true,
    pageSize: 1,
  })
  const pendingContacts = api.useGetContactsQuery({
    requiresCallback: true,
    pageSize: 1,
  })

  return (
    <Container size="xl">
      <Title order={1}>Enquiries</Title>
      <SimpleGrid cols={2} mt="lg">
        <PendingCard
          count={pendingCalls.data?.item_count}
          icon={<IconPhone stroke={1.5} />}
          noun={['call', 'calls']}
          selected={kind === 'call'}
          onClick={() => setKind('call')}
        />
        <PendingCard
          count={pendingContacts.data?.item_count}
          icon={<IconMail stroke={1.5} />}
          noun={['contact', 'contacts']}
          selected={kind === 'contact'}
          onClick={() => setKind('contact')}
        />
      </SimpleGrid>
      {/* Both stay mounted so each list keeps its filters and page. */}
      <Box display={kind === 'call' ? undefined : 'none'}>
        <CallTable topicOptions={CONTEXT.topic_options} />
      </Box>
      <Box display={kind === 'contact' ? undefined : 'none'}>
        <ContactTable />
      </Box>
    </Container>
  )
}

interface PendingCardProps {
  count?: number
  icon: React.ReactNode
  noun: [string, string]
  selected: boolean
  onClick: () => void
}

const PendingCard = ({
  count,
  icon,
  noun,
  selected,
  onClick,
}: PendingCardProps) => (
  <Paper
    component="button"
    type="button"
    withBorder
    p="md"
    onClick={onClick}
    aria-pressed={selected}
    style={{
      cursor: 'pointer',
      textAlign: 'left',
      borderWidth: selected ? 2 : 1,
      borderColor: selected ? 'var(--mantine-color-blue-6)' : undefined,
      backgroundColor: selected ? 'var(--mantine-color-blue-0)' : undefined,
    }}
  >
    <Group gap="md" wrap="nowrap">
      <ThemeIcon
        variant="light"
        color={selected ? 'blue' : 'gray'}
        size={44}
        radius="md"
      >
        {icon}
      </ThemeIcon>
      {count === 0 ? (
        <Text fz="lg">No {noun[1]} pending</Text>
      ) : (
        <div>
          <Text span fz={28} fw={700} mr="xs">
            {count ?? '-'}
          </Text>
          <Text span fz="lg">
            {count === 1 ? noun[0] : noun[1]} pending
          </Text>
        </div>
      )}
    </Group>
  </Paper>
)

mount(App)
