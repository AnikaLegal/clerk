import {
  Anchor,
  Group,
  HoverCard,
  Paper,
  Stack,
  Text,
  ThemeIcon,
} from '@mantine/core'
import {
  Icon,
  IconAlertTriangle,
  IconBan,
  IconBriefcase,
  IconFolder,
  IconUser,
} from '@tabler/icons-react'
import { Enquiry, EnquiryBlacklistMatch, EnquiryMatch } from 'api'
import { CASE_STATUS_COLORS } from 'consts'
import dayjs from 'dayjs'
import React from 'react'

const STYLES = {
  OPEN_CASE: { label: 'Open case', color: CASE_STATUS_COLORS.OPEN },
  FORMER_CLIENT: { label: 'Former client', color: CASE_STATUS_COLORS.CLOSED },
} as const

// The case page's colour for contact restrictions.
const DO_NOT_CONTACT_COLOR = 'orange'

const isDoNotContact = (match: EnquiryMatch) =>
  match.client.contact_restriction === 'DO_NOT_CONTACT'

const getMatchColor = (match: EnquiryMatch) =>
  isDoNotContact(match) ? DO_NOT_CONTACT_COLOR : STYLES[match.state].color

const formatMonth = (value: string) => dayjs(value).format('MMM YYYY')

type MatchedOn = EnquiryMatch['matched_on'][number]

const BLACKLIST_COLOR = 'red'

interface MatchedValueProps {
  value: string
  enquiry: Enquiry
  matchedOn: MatchedOn
}

// Shows each icon only beside the detail that matched.
export const MatchedValue = ({
  value,
  enquiry,
  matchedOn,
}: MatchedValueProps) => {
  const { blacklist, match } = enquiry
  const isBlacklisted = blacklist?.matched_on.includes(matchedOn)
  const isClient = match?.matched_on.includes(matchedOn)
  if (!isBlacklisted && !isClient) {
    return value
  }
  return (
    <Group gap={6} wrap="nowrap" justify="space-between">
      <span style={{ whiteSpace: 'nowrap' }}>{value}</span>
      <Group gap={4} wrap="nowrap">
        {isBlacklisted && blacklist && <BlacklistIcon blacklist={blacklist} />}
        {isClient && match && <ClientMatchIcon match={match} />}
      </Group>
    </Group>
  )
}

const BlacklistIcon = ({ blacklist }: { blacklist: EnquiryBlacklistMatch }) => (
  <HoverCard width={300} shadow="md" openDelay={100} withinPortal>
    <HoverCard.Target>
      <ThemeIcon
        size={18}
        radius="xl"
        color={BLACKLIST_COLOR}
        tabIndex={0}
        aria-label={`Blacklisted${blacklist.name ? `: ${blacklist.name}` : ''}`}
        style={{ cursor: 'default', flexShrink: 0 }}
      >
        <IconBan size={12} stroke={2.5} />
      </ThemeIcon>
    </HoverCard.Target>
    <HoverCard.Dropdown>
      <Stack gap={4}>
        <Text fz="xs" fw={700} c={`${BLACKLIST_COLOR}.7`} tt="uppercase">
          Blacklisted
        </Text>
        {blacklist.name && <Text fz="sm">{blacklist.name}</Text>}
        {blacklist.reason && (
          <Text fz="sm" style={{ whiteSpace: 'pre-wrap' }}>
            {blacklist.reason}
          </Text>
        )}
        <Text fz="xs" c="dimmed">
          Added {dayjs(blacklist.created_at).format('DD/MM/YY')}
          {blacklist.created_by_name && ` by ${blacklist.created_by_name}`}
        </Text>
      </Stack>
    </HoverCard.Dropdown>
  </HoverCard>
)

const ClientMatchIcon = ({ match }: { match: EnquiryMatch }) => {
  const { label, color } = STYLES[match.state]
  const { client, case: matchedCase } = match
  const isOpenCase = match.state === 'OPEN_CASE'

  return (
    <HoverCard width={300} shadow="md" openDelay={100} withinPortal>
      <HoverCard.Target>
        <ThemeIcon
          size={18}
          radius="xl"
          color={getMatchColor(match)}
          tabIndex={0}
          aria-label={[
            `${label}: ${client.full_name}`,
            isDoNotContact(match) && 'do not contact',
          ]
            .filter(Boolean)
            .join(', ')}
          style={{ cursor: 'default', flexShrink: 0 }}
        >
          <IconUser size={12} stroke={2.5} />
        </ThemeIcon>
      </HoverCard.Target>
      <HoverCard.Dropdown>
        <Stack gap={4}>
          <Text fz="xs" fw={700} c={`${color}.7`} tt="uppercase">
            {label}
          </Text>
          <IconRow icon={IconUser}>
            <Anchor href={client.url}>{client.full_name}</Anchor>
            {isOpenCase && (
              <Text span inherit c="dimmed">
                {` since ${formatMonth(client.created_at)}`}
              </Text>
            )}
          </IconRow>
          {matchedCase && (
            <>
              <IconRow icon={IconFolder}>
                <Anchor href={matchedCase.url}>{matchedCase.fileref}</Anchor>
                {` ${matchedCase.topic_display} · `}
                {matchedCase.closed_at
                  ? `Closed ${formatMonth(matchedCase.closed_at)}`
                  : matchedCase.stage_display}
              </IconRow>
              {isOpenCase && (
                <IconRow icon={IconBriefcase}>
                  {matchedCase.paralegal_name ?? (
                    <Text span inherit c="dimmed">
                      No paralegal
                    </Text>
                  )}
                </IconRow>
              )}
            </>
          )}
          <ContactRestriction match={match} />
        </Stack>
      </HoverCard.Dropdown>
    </HoverCard>
  )
}

// The client's contact restriction and notes, as the case page shows them.
const ContactRestriction = ({ match }: { match: EnquiryMatch }) => {
  const { contact_restriction_display: restriction, contact_notes: notes } =
    match.client
  if (isDoNotContact(match)) {
    return (
      <Paper
        withBorder
        p="xs"
        mt={4}
        bg="var(--mantine-color-orange-0)"
        bd="1px solid var(--mantine-color-orange-4)"
        c="var(--mantine-color-orange-9)"
      >
        <Group gap={6} wrap="nowrap">
          <IconAlertTriangle size={16} stroke={1.8} aria-hidden />
          <Text fz="sm" fw={700}>
            {restriction}
          </Text>
        </Group>
        {notes && <NotesText>{notes}</NotesText>}
      </Paper>
    )
  }
  if (!restriction && !notes) {
    return null
  }
  return (
    <Paper withBorder p="xs" mt={4} bg="var(--mantine-color-gray-0)">
      <Text fz="sm" fw={700}>
        {restriction ?? 'Contact notes'}
      </Text>
      {notes && <NotesText>{notes}</NotesText>}
    </Paper>
  )
}

const NotesText = ({ children }: { children: React.ReactNode }) => (
  <Text fz="sm" mt={2} style={{ whiteSpace: 'pre-wrap' }}>
    {children}
  </Text>
)

interface IconRowProps {
  icon: Icon
  children: React.ReactNode
}

const IconRow = ({ icon: RowIcon, children }: IconRowProps) => (
  <Group gap={8} wrap="nowrap" align="flex-start">
    <RowIcon
      size={16}
      stroke={1.5}
      color="var(--mantine-color-dimmed)"
      style={{ flexShrink: 0, marginTop: 2 }}
      aria-hidden
    />
    <Text fz="sm">{children}</Text>
  </Group>
)
