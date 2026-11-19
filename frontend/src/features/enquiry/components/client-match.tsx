import { Anchor, Group, HoverCard, Stack, Text, ThemeIcon } from '@mantine/core'
import { Icon, IconBriefcase, IconFolder, IconUser } from '@tabler/icons-react'
import { EnquiryMatch } from 'api'
import { CASE_STATUS_COLORS } from 'consts'
import dayjs from 'dayjs'
import React from 'react'

const STYLES = {
  OPEN_CASE: { label: 'Open case', color: CASE_STATUS_COLORS.OPEN },
  FORMER_CLIENT: { label: 'Former client', color: CASE_STATUS_COLORS.CLOSED },
} as const

const formatMonth = (value: string) => dayjs(value).format('MMM YYYY')

type MatchedOn = EnquiryMatch['matched_on'][number]

// Inset shadow rather than a border, so the table's own borders stay intact.
export const getMatchEdgeStyle = (
  match: EnquiryMatch | null
): React.CSSProperties | undefined =>
  match
    ? {
        boxShadow: `inset 4px 0 0 var(--mantine-color-${STYLES[match.state].color}-6)`,
      }
    : undefined

interface MatchedValueProps {
  value: string
  match: EnquiryMatch | null
  matchedOn: MatchedOn
}

// Shows the icon only beside the detail that matched.
export const MatchedValue = ({ value, match, matchedOn }: MatchedValueProps) =>
  match?.matched_on.includes(matchedOn) ? (
    <Group gap={6} wrap="nowrap" justify="space-between">
      <span style={{ whiteSpace: 'nowrap' }}>{value}</span>
      <ClientMatchIcon match={match} />
    </Group>
  ) : (
    value
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
          color={color}
          tabIndex={0}
          aria-label={`${label}: ${client.full_name}`}
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
                  ? `closed ${formatMonth(matchedCase.closed_at)}`
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
        </Stack>
      </HoverCard.Dropdown>
    </HoverCard>
  )
}

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
