import {
  ActionIcon,
  Box,
  Button,
  Drawer,
  Group,
  Loader,
  Paper,
  Stack,
  Text,
  TextInput,
  Tooltip,
} from '@mantine/core'
import { useForm } from '@mantine/form'
import { IconPencil } from '@tabler/icons-react'
import api, { Callback, Enquiry } from 'api'
import dayjs from 'dayjs'
import { yupResolver } from 'mantine-form-yup-resolver'
import { enqueueSnackbar } from 'notistack'
import React, { useState } from 'react'
import { getAPIErrorMessage } from 'utils'
import { PersonDetails, personSchema } from '../schema'
import type { EnquiryDetail } from './enquiry-table'

export interface EditablePerson {
  values: PersonDetails
  isRequired: boolean
  onSave: (person: PersonDetails) => Promise<unknown>
}

export interface HistoryDrawerTarget {
  enquiry: Enquiry
  details: EnquiryDetail[]
  // The name and email, which staff can correct here.
  person: EditablePerson
}

interface HistoryDrawerProps {
  target: HistoryDrawerTarget | null
  onClose: () => void
}

const formatTime = (value: string) => dayjs(value).format('DD/MM/YY [at] hA')

export const HistoryDrawer = ({ target, onClose }: HistoryDrawerProps) => (
  <Drawer
    opened={target !== null}
    onClose={onClose}
    position="right"
    size="md"
    title={
      <Text fw={700} fz="lg">
        Callback history
      </Text>
    }
  >
    {target && (
      <>
        <DetailsSection key={target.enquiry.id} target={target} />
        <History target={target} />
      </>
    )}
  </Drawer>
)

const DetailsSection = ({ target }: { target: HistoryDrawerTarget }) => {
  const [isEditing, setIsEditing] = useState(false)

  if (isEditing) {
    return (
      <PersonForm person={target.person} onDone={() => setIsEditing(false)} />
    )
  }
  return (
    <Group justify="space-between" align="flex-start" wrap="nowrap">
      <Details rows={target.details} />
      <Tooltip label="Edit name and email" openDelay={750}>
        <ActionIcon
          variant="transparent"
          color="gray"
          aria-label="Edit name and email"
          onClick={() => setIsEditing(true)}
        >
          <IconPencil stroke={1.5} />
        </ActionIcon>
      </Tooltip>
    </Group>
  )
}

interface PersonFormProps {
  person: EditablePerson
  onDone: () => void
}

const PersonForm = ({ person, onDone }: PersonFormProps) => {
  const form = useForm<PersonDetails>({
    mode: 'uncontrolled',
    validate: yupResolver(personSchema(person.isRequired)),
    initialValues: person.values,
  })

  const handleSubmit = (values: PersonDetails) =>
    person
      .onSave(values)
      .then(onDone)
      .catch((e) =>
        enqueueSnackbar(
          getAPIErrorMessage(e, 'Failed to save name and email'),
          {
            variant: 'error',
          }
        )
      )

  return (
    <form autoComplete="off" onSubmit={form.onSubmit(handleSubmit)}>
      <TextInput
        {...form.getInputProps('name')}
        key={form.key('name')}
        label="Name"
        autoComplete="off"
        data-autofocus
      />
      <TextInput
        {...form.getInputProps('email')}
        key={form.key('email')}
        label="Email"
        mt="sm"
        autoComplete="off"
      />
      <Group justify="right" mt="sm">
        <Button variant="default" onClick={onDone} disabled={form.submitting}>
          Cancel
        </Button>
        <Button
          type="submit"
          disabled={form.submitting}
          loading={form.submitting}
        >
          Save
        </Button>
      </Group>
    </form>
  )
}

// Labels in a narrow column beside their values.
const Details = ({ rows }: { rows: EnquiryDetail[] }) => (
  <Box
    fz="sm"
    style={{
      display: 'grid',
      gridTemplateColumns: 'auto 1fr',
      gap: '2px 12px',
    }}
  >
    {rows.map(([label, value]) => (
      <React.Fragment key={label}>
        <Text inherit c="dimmed">
          {label}
        </Text>
        <Text inherit style={{ whiteSpace: 'pre-wrap' }}>
          {value}
        </Text>
      </React.Fragment>
    ))}
  </Box>
)

const History = ({ target }: { target: HistoryDrawerTarget }) => {
  const { enquiry: record } = target
  const result = api.useGetCallbacksQuery({ enquiry: record.id })

  if (result.isLoading) {
    return <Loader mt="lg" />
  }
  if (result.isError) {
    return (
      <Text c="red" mt="lg">
        Could not load the history
      </Text>
    )
  }

  const callbacks = result.data ?? []
  // Counts carried over from before callbacks were logged with details.
  const unlogged = Math.max(0, record.number_callbacks - callbacks.length)
  return (
    <>
      <SectionTitle>Callbacks ({record.number_callbacks})</SectionTitle>
      {callbacks.length === 0 ? (
        <Text c="dimmed" fz="sm">
          {unlogged ? 'No callbacks logged with details' : 'No callbacks yet'}
        </Text>
      ) : (
        <Stack gap="sm">
          {callbacks.map((callback) => (
            <CallbackCard key={callback.id} callback={callback} />
          ))}
        </Stack>
      )}
      {(unlogged > 0 || record.comments) && (
        <TimelineCard
          title="Earlier"
          label={
            unlogged > 0 &&
            `${unlogged} ${unlogged === 1 ? 'callback' : 'callbacks'} with no details`
          }
          color={GREY_HEADER}
          mt="sm"
        >
          {record.comments && (
            <Text fz="sm" style={{ whiteSpace: 'pre-wrap' }}>
              {record.comments}
            </Text>
          )}
        </TimelineCard>
      )}
    </>
  )
}

// Header colours echo the case timeline's labels.
const GREEN_HEADER = { bg: 'green.6', c: 'white' }
const GREY_HEADER = { bg: 'gray.2', c: 'gray.7' }

interface TimelineCardProps {
  title: React.ReactNode
  detail?: string
  label?: React.ReactNode
  color: { bg: string; c: string }
  mt?: string
  children?: React.ReactNode
}

// A card in the style of the case page's timeline items.
const TimelineCard = ({
  title,
  detail,
  label,
  color,
  mt,
  children,
}: TimelineCardProps) => (
  <Paper withBorder shadow="xs" mt={mt} style={{ overflow: 'hidden' }}>
    <Group
      justify="space-between"
      gap="xs"
      wrap="nowrap"
      px="sm"
      py={6}
      fz="xs"
      fw={700}
      bg={color.bg}
      c={color.c}
    >
      <Text inherit>
        {title}
        {detail && (
          <Text span inherit fw={400} ml="xs" opacity={0.85}>
            {detail}
          </Text>
        )}
      </Text>
      {label && <Text inherit>{label}</Text>}
    </Group>
    {children && <Box p="sm">{children}</Box>}
  </Paper>
)

const SectionTitle = ({ children }: { children: React.ReactNode }) => (
  <Text fw={700} fz="sm" mt="lg" mb="xs">
    {children}
  </Text>
)

const CallbackCard = ({ callback }: { callback: Callback }) => {
  const fields: EnquiryDetail[] = [
    ['Purpose', callback.purpose],
    ['Summary', callback.summary],
    ['Action items', callback.action_items],
  ]
  const filled = fields.filter(([, value]) => value)

  return (
    <TimelineCard
      title={callback.logged_by_name ?? 'Unknown'}
      detail={formatTime(callback.created_at)}
      label={callback.is_answered ? 'Answered' : 'No answer'}
      color={callback.is_answered ? GREEN_HEADER : GREY_HEADER}
    >
      {callback.is_answered
        ? filled.length > 0 && (
            <Stack gap={6}>
              {filled.map(([label, value]) => (
                <Box key={label} fz="sm">
                  <Text inherit c="dimmed" fz="xs">
                    {label}
                  </Text>
                  <MultilineText>{value}</MultilineText>
                </Box>
              ))}
            </Stack>
          )
        : callback.summary && (
            <Box fz="sm">
              <MultilineText>{callback.summary}</MultilineText>
            </Box>
          )}
    </TimelineCard>
  )
}

const MultilineText = ({ children }: { children: React.ReactNode }) => (
  <Text inherit style={{ whiteSpace: 'pre-wrap' }}>
    {children}
  </Text>
)
