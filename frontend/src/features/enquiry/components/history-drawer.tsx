import {
  ActionIcon,
  Badge,
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
import api, { Call, Callback, Contact } from 'api'
import dayjs from 'dayjs'
import { yupResolver } from 'mantine-form-yup-resolver'
import { enqueueSnackbar } from 'notistack'
import React, { useState } from 'react'
import { getAPIErrorMessage } from 'utils'
import { PersonDetails, personSchema } from '../schema'
import type { EnquiryDetail, EnquiryKind } from './enquiry-table'

export interface EditablePerson {
  values: PersonDetails
  isRequired: boolean
  onSave: (person: PersonDetails) => Promise<unknown>
}

export interface HistoryDrawerTarget {
  kind: EnquiryKind
  record: Call | Contact
  details: EnquiryDetail[]
  // The name and email, which staff can correct here.
  person: EditablePerson
}

interface HistoryDrawerProps {
  target: HistoryDrawerTarget | null
  onClose: () => void
}

const formatTime = (value: string) => dayjs(value).format('DD/MM/YY h:mma')

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
        <DetailsSection key={target.record.id} target={target} />
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
  const { kind, record } = target
  const result = api.useGetCallbacksQuery(
    kind === 'call' ? { call: record.id } : { contact: record.id }
  )

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
        <>
          <SectionTitle>Earlier</SectionTitle>
          <Paper withBorder p="sm" bg="var(--mantine-color-gray-0)">
            {unlogged > 0 && (
              <Text fz="sm" c="dimmed">
                {unlogged} {unlogged === 1 ? 'callback' : 'callbacks'} with no
                details
              </Text>
            )}
            {record.comments && (
              <Text
                fz="sm"
                mt={unlogged > 0 ? 'xs' : 0}
                style={{ whiteSpace: 'pre-wrap' }}
              >
                {record.comments}
              </Text>
            )}
          </Paper>
        </>
      )}
    </>
  )
}

const SectionTitle = ({ children }: { children: React.ReactNode }) => (
  <Text fw={700} fz="sm" mt="lg" mb="xs">
    {children}
  </Text>
)

const CallbackCard = ({ callback }: { callback: Callback }) => {
  const fields: EnquiryDetail[] = callback.is_answered
    ? [
        ['Purpose', callback.purpose],
        ['Summary', callback.summary],
        ['Actions', callback.action_items],
      ]
    : [['Note', callback.summary]]
  const filled = fields.filter(([, value]) => value)

  return (
    <Paper withBorder p="sm">
      <Group justify="space-between" gap="xs" wrap="nowrap">
        <Badge
          variant="light"
          color={callback.is_answered ? 'green' : 'gray'}
          radius="sm"
        >
          {callback.is_answered ? 'Answered' : 'No answer'}
        </Badge>
        <Text fz="xs" c="dimmed">
          {[formatTime(callback.created_at), callback.logged_by_name]
            .filter(Boolean)
            .join(' · ')}
        </Text>
      </Group>
      {filled.length > 0 && (
        <Box mt="xs">
          <Details rows={filled} />
        </Box>
      )}
    </Paper>
  )
}
