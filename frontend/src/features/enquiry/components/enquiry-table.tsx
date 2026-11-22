import {
  Center,
  Group,
  Loader,
  Pagination,
  Select,
  Switch,
  Table,
  Text,
} from '@mantine/core'
import {
  IconArrowBackUp,
  IconCheck,
  IconHistory,
  IconPhoneCheck,
  IconPhoneX,
} from '@tabler/icons-react'
import api, { Enquiry, EnquirySource, GetEnquiriesApiArg } from 'api'
import { ActionIconWithConfirmation } from 'comps/action-icon'
import dayjs from 'dayjs'
import { enqueueSnackbar } from 'notistack'
import React, { useEffect, useState } from 'react'
import { ErrorResult, getAPIErrorMessage } from 'utils'
import { PersonDetails } from '../schema'
import { CallbackModal, CallbackModalTarget } from './callback-modal'
import { getMatchEdgeStyle, MatchedValue } from './client-match'
import { HistoryDrawer, HistoryDrawerTarget } from './history-drawer'

export type EnquiryDetail = [label: string, value: string]

const formatTime = (value: string) => dayjs(value).format('DD/MM/YY h:mma')

const NO_WRAP = { whiteSpace: 'nowrap' } as const

const HEADERS = [
  'Received',
  'From',
  'Name',
  'Email',
  'Phone number',
  'Callbacks',
  'Latest',
  '',
]

const SOURCE_OPTIONS: { value: EnquirySource; label: string }[] = [
  { value: 'CALL', label: 'Call' },
  { value: 'CONTACT_FORM', label: 'Contact form' },
]

// The changes staff make from the table and drawer.
type EnquiryChange = Partial<PersonDetails> & { requires_callback?: boolean }

export const EnquiryTable = () => {
  const [args, setArgs] = useState<GetEnquiriesApiArg>({
    requiresCallback: true,
    page: 1,
  })
  // Picks up new enquiries and colleagues' callbacks when staff come back.
  const result = api.useGetEnquiriesQuery(args, { refetchOnFocus: true })
  const now = useNow()
  const [updateEnquiry] = api.useUpdateEnquiryMutation()
  const save = (id: number, enquiryUpdate: EnquiryChange) =>
    updateEnquiry({ id, enquiryUpdate }).unwrap()

  const page = args.page || 1
  const results = result.data?.results
  const [callbackTarget, setCallbackTarget] =
    useState<CallbackModalTarget | null>(null)
  const [historyEnquiry, setHistoryEnquiry] = useState<Enquiry | null>(null)

  const logCallback = (enquiry: Enquiry, isAnswered: boolean) =>
    setCallbackTarget({
      enquiry,
      isAnswered,
      details: describe(enquiry)
        .map(([, value]) => value)
        .join(' · '),
    })
  // The row from the latest fetch, so the drawer shows edits once saved.
  const historyFresh =
    historyEnquiry &&
    (results?.find((enquiry) => enquiry.id === historyEnquiry.id) ??
      historyEnquiry)
  const historyTarget: HistoryDrawerTarget | null = historyFresh && {
    enquiry: historyFresh,
    details: describe(historyFresh),
    person: {
      values: { name: historyFresh.name, email: historyFresh.email },
      // A contact typed both in; a caller may have given neither.
      isRequired: historyFresh.source === 'CONTACT_FORM',
      onSave: (person) =>
        save(historyFresh.id, person).then(() =>
          enqueueSnackbar('Name and email saved', { variant: 'success' })
        ),
    },
  }

  // A save can empty the last page, which the API then answers with a 404;
  // step back a page rather than show an error.
  const isPastLastPage =
    result.isError && (result.error as ErrorResult)?.status === 404 && page > 1
  useEffect(() => {
    if (isPastLastPage) {
      setArgs((prev) => ({ ...prev, page: page - 1 }))
    }
  }, [isPastLastPage, page, setArgs])

  useEffect(() => {
    if (result.isError && !isPastLastPage) {
      enqueueSnackbar(
        getAPIErrorMessage(
          result.error as ErrorResult,
          'Could not load enquiries'
        ),
        { variant: 'error' }
      )
    }
  }, [result.isError, result.error, isPastLastPage])

  const handleFilterChange = (key: string, value: unknown) =>
    setArgs((prev) => ({ ...prev, [key]: value ?? undefined, page: 1 }))

  const saveWithMessage = (id: number, update: EnquiryChange, ok: string) =>
    save(id, update)
      .then(() => enqueueSnackbar(ok, { variant: 'success' }))
      .catch((e) => {
        enqueueSnackbar(getAPIErrorMessage(e, 'Failed to update enquiry'), {
          variant: 'error',
        })
        throw e
      })

  return (
    <>
      <Group mt="xl" gap="lg" align="flex-end">
        <Select
          label="From"
          placeholder="All"
          size="md"
          data={SOURCE_OPTIONS}
          value={args.source ?? null}
          onChange={(value) => handleFilterChange('source', value)}
          clearable
          allowDeselect
          withCheckIcon={false}
          w={200}
        />
        <Switch
          label="Show done"
          size="md"
          // Centres it on the select's input rather than its label.
          mb={9}
          // Its label otherwise spans the full width, so the whole row toggles.
          w="fit-content"
          checked={args.requiresCallback === undefined}
          onChange={(e) =>
            handleFilterChange(
              'requiresCallback',
              e.currentTarget.checked ? undefined : true
            )
          }
        />
      </Group>
      <Table
        withColumnBorders
        withTableBorder
        verticalSpacing="xs"
        fz="md"
        mt="md"
      >
        <Table.Thead>
          <Table.Tr>
            {HEADERS.map((header, i) => (
              <Table.Th key={i} w={header ? undefined : '1%'}>
                {header}
              </Table.Th>
            ))}
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>
          {result.isLoading ? (
            <MessageRow>
              <Loader />
            </MessageRow>
          ) : result.isError ? (
            <MessageRow>
              <Text c="red">Could not load enquiries</Text>
            </MessageRow>
          ) : !results || results.length === 0 ? (
            <MessageRow>No enquiries found</MessageRow>
          ) : (
            results.map((enquiry) => (
              <Table.Tr
                key={enquiry.id}
                c={enquiry.requires_callback ? undefined : 'dimmed'}
              >
                <Table.Td style={{ ...NO_WRAP, ...getMatchEdgeStyle(enquiry) }}>
                  {dayjs(enquiry.created_at).format('DD/MM/YY')}
                  <Text inherit c="dimmed" fz="sm">
                    {dayjs(enquiry.created_at).format('h:mma')}
                  </Text>
                </Table.Td>
                <Table.Td style={NO_WRAP}>{describeSource(enquiry)}</Table.Td>
                <Table.Td>{enquiry.name}</Table.Td>
                <Table.Td>
                  <MatchedValue
                    value={enquiry.email}
                    enquiry={enquiry}
                    matchedOn="EMAIL"
                  />
                </Table.Td>
                <Table.Td>
                  <MatchedValue
                    value={enquiry.phone}
                    enquiry={enquiry}
                    matchedOn="PHONE"
                  />
                </Table.Td>
                <Table.Td>{enquiry.number_callbacks}</Table.Td>
                <Table.Td>
                  <LatestCell record={enquiry} now={now} />
                </Table.Td>
                <Table.Td>
                  <RowActions
                    record={enquiry}
                    save={saveWithMessage}
                    onShowHistory={() => setHistoryEnquiry(enquiry)}
                    onLogCallback={(isAnswered) =>
                      logCallback(enquiry, isAnswered)
                    }
                  />
                </Table.Td>
              </Table.Tr>
            ))
          )}
        </Table.Tbody>
      </Table>
      {result.data && result.data.page_count > 1 && (
        <Pagination
          total={result.data.page_count}
          value={page}
          onChange={(value) => setArgs((prev) => ({ ...prev, page: value }))}
          mt="md"
          withEdges
          withControls
        />
      )}
      <CallbackModal
        target={callbackTarget}
        onClose={() => setCallbackTarget(null)}
      />
      <HistoryDrawer
        target={historyTarget}
        onClose={() => setHistoryEnquiry(null)}
      />
    </>
  )
}

const describeSource = (enquiry: Enquiry) =>
  [enquiry.source_display, enquiry.topic_display].filter(Boolean).join(' · ')

// Labelled details that identify the enquiry in the modal and drawer.
const describe = (enquiry: Enquiry): EnquiryDetail[] =>
  (
    [
      ['From', describeSource(enquiry)],
      ['Name', enquiry.name],
      ['Email', enquiry.email],
      ['Phone', enquiry.phone],
      ['Received', formatTime(enquiry.created_at)],
    ] as EnquiryDetail[]
  ).filter(([, value]) => value)

// The latest callback, or comments recorded before callbacks were logged.
// The current time, ticking once a minute so the ages stay current.
const useNow = () => {
  const [now, setNow] = useState(() => dayjs())
  useEffect(() => {
    const id = setInterval(() => setNow(dayjs()), 60_000)
    return () => clearInterval(id)
  }, [])
  return now
}

interface LatestCellProps {
  record: Enquiry
  now: dayjs.Dayjs
}

const LatestCell = ({ record, now }: LatestCellProps) => {
  const latest = record.latest_callback
  if (!latest) {
    return record.comments ? <CellText>{record.comments}</CellText> : null
  }
  return (
    <>
      <Text inherit c="dimmed" fz="sm" title={formatTime(latest.created_at)}>
        {latest.is_answered ? 'Answered' : 'No answer'} ·{' '}
        {formatAge(latest.created_at, now)}
      </Text>
      {latest.summary && <CellText>{latest.summary}</CellText>}
    </>
  )
}

const CellText = ({ children }: { children: React.ReactNode }) => (
  <Text inherit lineClamp={3} style={{ whiteSpace: 'pre-wrap' }}>
    {children}
  </Text>
)

// How long ago, in the largest whole unit: 5m, 3h or 2d ago.
const formatAge = (value: string, now: dayjs.Dayjs) => {
  const minutes = now.diff(value, 'minute')
  if (minutes < 60) {
    return minutes < 1 ? 'just now' : `${minutes}m ago`
  }
  const hours = Math.floor(minutes / 60)
  return hours < 24 ? `${hours}h ago` : `${Math.floor(hours / 24)}d ago`
}

const MessageRow = ({ children }: { children: React.ReactNode }) => (
  <Table.Tr>
    <Table.Td colSpan={HEADERS.length}>
      <Center m="sm">{children}</Center>
    </Table.Td>
  </Table.Tr>
)

interface RowActionsProps {
  record: Enquiry
  save: (id: number, update: EnquiryChange, ok: string) => Promise<unknown>
  onShowHistory: () => void
  onLogCallback: (isAnswered: boolean) => void
}

// Answered and No answer match the history drawer's header colours.
const tinted = (color: string) => ({ variant: 'light', color, size: 'lg' })

const RowActions = ({
  record,
  save,
  onShowHistory,
  onLogCallback,
}: RowActionsProps) => {
  const [isBusy, setIsBusy] = useState(false)
  const isDone = !record.requires_callback

  // Stays disabled until the refreshed row arrives, so a second click can't
  // toggle the flag back before the list catches up.
  useEffect(() => setIsBusy(false), [record.modified_at])

  const label = isDone ? 'Mark pending' : 'Mark done'
  const handleClick = () => {
    setIsBusy(true)
    save(
      record.id,
      { requires_callback: isDone },
      isDone ? 'Marked pending' : 'Marked done'
    ).catch(() => setIsBusy(false))
  }

  return (
    <ActionIconWithConfirmation.Group gap={4}>
      <ActionIconWithConfirmation
        tooltip={{ label: 'Log answered call' }}
        icon={<IconPhoneCheck stroke={1.5} />}
        actionIcon={{ ...tinted('green'), 'aria-label': 'Log answered call' }}
        onClick={() => onLogCallback(true)}
      />
      <ActionIconWithConfirmation
        tooltip={{ label: 'Log missed call' }}
        icon={<IconPhoneX stroke={1.5} />}
        actionIcon={{ ...tinted('gray'), 'aria-label': 'Log missed call' }}
        onClick={() => onLogCallback(false)}
      />
      <ActionIconWithConfirmation
        tooltip={{ label: 'Callback history' }}
        icon={<IconHistory stroke={1.5} />}
        actionIcon={{ ...tinted('blue'), 'aria-label': 'Callback history' }}
        onClick={onShowHistory}
      />
      <ActionIconWithConfirmation
        tooltip={{ label }}
        icon={
          isDone ? <IconArrowBackUp stroke={1.5} /> : <IconCheck stroke={1.5} />
        }
        actionIcon={{
          ...tinted('green'),
          'aria-label': label,
          loading: isBusy,
          disabled: isBusy,
        }}
        onClick={handleClick}
        confirmButton={{
          label: isDone ? 'Confirm pending' : 'Confirm done',
          color: 'green',
        }}
      />
    </ActionIconWithConfirmation.Group>
  )
}
