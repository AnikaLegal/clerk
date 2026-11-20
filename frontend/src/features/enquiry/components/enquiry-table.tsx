import { Center, Loader, Pagination, Switch, Table, Text } from '@mantine/core'
import {
  IconArrowBackUp,
  IconCheck,
  IconHistory,
  IconPhoneCheck,
  IconPhoneX,
} from '@tabler/icons-react'
import api, { Call, Contact, GetCallsApiArg, GetContactsApiArg } from 'api'
import { ActionIconWithConfirmation } from 'comps/action-icon'
import dayjs from 'dayjs'
import { enqueueSnackbar } from 'notistack'
import React, { useEffect, useState } from 'react'
import { ErrorResult, getAPIErrorMessage } from 'utils'
import { CallbackModal, CallbackModalTarget } from './callback-modal'
import { getMatchEdgeStyle, MatchedValue } from './client-match'
import { PersonDetails } from '../schema'
import { HistoryDrawer, HistoryDrawerTarget } from './history-drawer'

export type EnquiryKind = 'call' | 'contact'

export type EnquiryDetail = [label: string, value: string]

const formatTime = (value: string) => dayjs(value).format('DD/MM/YY h:mma')

const NO_WRAP = { whiteSpace: 'nowrap' } as const

const DEFAULT_ARGS = { requiresCallback: true, page: 1 }

// Marks an enquiry done or pending; the one change made from the table.
type DoneUpdate = { requires_callback: boolean }
type Save = (id: number, update: DoneUpdate) => Promise<unknown>
type SavePerson = (id: number, person: PersonDetails) => Promise<unknown>

export const CallTable = () => {
  const [args, setArgs] = useState<GetCallsApiArg>(DEFAULT_ARGS)
  const result = api.useGetCallsQuery(args)
  const [updateCall] = api.useUpdateCallMutation()
  const save: Save = (id, update) =>
    updateCall({ id, callUpdate: update }).unwrap()
  const savePerson: SavePerson = (id, { name, email }) =>
    updateCall({
      id,
      callUpdate: { caller_name: name, caller_email: email },
    }).unwrap()

  return (
    <EnquiryTable<Call>
      kind="call"
      person={(call) => ({ name: call.caller_name, email: call.caller_email })}
      isPersonRequired={false}
      savePerson={savePerson}
      describe={(call) => [
        ['Name', call.caller_name],
        ['Email', call.caller_email],
        ['Phone', call.phone_number],
        ['Topic', call.topic_display],
      ]}
      args={args}
      setArgs={setArgs}
      result={result}
      save={save}
      headers={['Received', 'Name', 'Email', 'Phone number', 'Topic']}
      cells={(call) => [
        formatTime(call.created_at),
        call.caller_name,
        call.caller_email,
        <MatchedValue
          key="phone"
          value={call.phone_number}
          match={call.match}
          matchedOn="PHONE"
        />,
        call.topic_display,
      ]}
    />
  )
}

export const ContactTable = () => {
  const [args, setArgs] = useState<GetContactsApiArg>(DEFAULT_ARGS)
  const result = api.useGetContactsQuery(args)
  const [updateContact] = api.useUpdateContactMutation()
  const save: Save = (id, update) =>
    updateContact({ id, contactUpdate: update }).unwrap()
  const savePerson: SavePerson = (id, person) =>
    updateContact({ id, contactUpdate: person }).unwrap()

  return (
    <EnquiryTable<Contact>
      kind="contact"
      person={(contact) => ({ name: contact.name, email: contact.email })}
      isPersonRequired
      savePerson={savePerson}
      describe={(contact) => [
        ['Name', contact.name],
        ['Email', contact.email],
        ['Phone', contact.phone],
      ]}
      args={args}
      setArgs={setArgs}
      result={result}
      save={save}
      headers={['Received', 'Name', 'Email', 'Phone number', 'Referral']}
      cells={(contact) => [
        formatTime(contact.created_at),
        contact.name,
        <MatchedValue
          key="email"
          value={contact.email}
          match={contact.match}
          matchedOn="EMAIL"
        />,
        <MatchedValue
          key="phone"
          value={contact.phone}
          match={contact.match}
          matchedOn="PHONE"
        />,
        contact.referral,
      ]}
    />
  )
}

interface ListArgs {
  requiresCallback?: boolean
  page?: number
}

interface ListResult<T> {
  data?: { results: T[]; page_count: number }
  isLoading: boolean
  isError: boolean
  error?: unknown
}

interface EnquiryTableProps<T extends Call | Contact> {
  kind: EnquiryKind
  // Labelled details that identify the enquiry in the modal and drawer.
  describe: (record: T) => EnquiryDetail[]
  args: ListArgs
  setArgs: React.Dispatch<React.SetStateAction<ListArgs>>
  result: ListResult<T>
  save: Save
  // The name and email shown in the drawer, and how to correct them.
  person: (record: T) => PersonDetails
  isPersonRequired: boolean
  savePerson: SavePerson
  headers: string[]
  cells: (record: T) => React.ReactNode[]
}

const EnquiryTable = <T extends Call | Contact>({
  kind,
  describe,
  args,
  setArgs,
  result,
  save,
  person,
  isPersonRequired,
  savePerson,
  headers,
  cells,
}: EnquiryTableProps<T>) => {
  const page = args.page || 1
  const columnCount = headers.length + 4

  const results = result.data?.results
  const [callbackTarget, setCallbackTarget] =
    useState<CallbackModalTarget | null>(null)
  const [historyRecord, setHistoryRecord] = useState<T | null>(null)

  const details = (record: T): EnquiryDetail[] => [
    ...describe(record).filter(([, value]) => value),
    ['Received', formatTime(record.created_at)],
  ]
  const logCallback = (record: T, isAnswered: boolean) =>
    setCallbackTarget({
      kind,
      record,
      isAnswered,
      details: details(record)
        .map(([, value]) => value)
        .join(' · '),
    })
  // The row from the latest fetch, so the drawer shows edits once saved.
  const historyFresh =
    historyRecord &&
    (results?.find((record) => record.id === historyRecord.id) ?? historyRecord)
  const historyTarget: HistoryDrawerTarget | null = historyFresh && {
    kind,
    record: historyFresh,
    details: details(historyFresh),
    person: {
      values: person(historyFresh),
      isRequired: isPersonRequired,
      onSave: (details) =>
        savePerson(historyFresh.id, details).then(() =>
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

  const saveWithMessage = (id: number, update: DoneUpdate, ok: string) =>
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
      <Switch
        label="Show done"
        size="md"
        mt="xl"
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
      <Table
        withColumnBorders
        withTableBorder
        verticalSpacing="xs"
        fz="md"
        mt="md"
      >
        <Table.Thead>
          <Table.Tr>
            {headers.map((header) => (
              <Table.Th key={header}>{header}</Table.Th>
            ))}
            <Table.Th>Callbacks</Table.Th>
            <Table.Th>Latest</Table.Th>
            <Table.Th>Updated</Table.Th>
            <Table.Th w="1%"></Table.Th>
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>
          {result.isLoading ? (
            <MessageRow columnCount={columnCount}>
              <Loader />
            </MessageRow>
          ) : result.isError ? (
            <MessageRow columnCount={columnCount}>
              <Text c="red">Could not load enquiries</Text>
            </MessageRow>
          ) : !results || results.length === 0 ? (
            <MessageRow columnCount={columnCount}>
              No enquiries found
            </MessageRow>
          ) : (
            results.map((record) => (
              <Table.Tr
                key={record.id}
                c={record.requires_callback ? undefined : 'dimmed'}
              >
                {cells(record).map((cell, i) => (
                  <Table.Td
                    key={headers[i]}
                    // Received is always the first column.
                    style={
                      i === 0
                        ? { ...NO_WRAP, ...getMatchEdgeStyle(record.match) }
                        : undefined
                    }
                  >
                    {cell}
                  </Table.Td>
                ))}
                <Table.Td>{record.number_callbacks}</Table.Td>
                <Table.Td>
                  <LatestCell record={record} />
                </Table.Td>
                <Table.Td style={NO_WRAP}>
                  {formatTime(record.modified_at)}
                </Table.Td>
                <Table.Td>
                  <RowActions
                    record={record}
                    save={saveWithMessage}
                    onShowHistory={() => setHistoryRecord(record)}
                    onLogCallback={(isAnswered) =>
                      logCallback(record, isAnswered)
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
        onClose={() => setHistoryRecord(null)}
      />
    </>
  )
}

// The latest callback, or comments recorded before callbacks were logged.
const LatestCell = ({ record }: { record: Call | Contact }) => {
  const latest = record.latest_callback
  const text = latest
    ? [latest.is_answered ? 'Answered' : 'No answer', latest.summary]
        .filter(Boolean)
        .join(' · ')
    : record.comments
  if (!text) {
    return null
  }
  return (
    <Text inherit lineClamp={3} style={{ whiteSpace: 'pre-wrap' }}>
      {text}
    </Text>
  )
}

const MessageRow = ({
  columnCount,
  children,
}: {
  columnCount: number
  children: React.ReactNode
}) => (
  <Table.Tr>
    <Table.Td colSpan={columnCount}>
      <Center m="sm">{children}</Center>
    </Table.Td>
  </Table.Tr>
)

interface RowActionsProps {
  record: Call | Contact
  save: (id: number, update: DoneUpdate, ok: string) => Promise<unknown>
  onShowHistory: () => void
  onLogCallback: (isAnswered: boolean) => void
}

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
    <ActionIconWithConfirmation.Group>
      <ActionIconWithConfirmation
        tooltip={{ label: 'Log answered call' }}
        icon={<IconPhoneCheck stroke={1.5} />}
        actionIcon={{ 'aria-label': 'Log answered call' }}
        onClick={() => onLogCallback(true)}
      />
      <ActionIconWithConfirmation
        tooltip={{ label: 'Log missed call' }}
        icon={<IconPhoneX stroke={1.5} />}
        actionIcon={{ 'aria-label': 'Log missed call' }}
        onClick={() => onLogCallback(false)}
      />
      <ActionIconWithConfirmation
        tooltip={{ label: 'Callback history' }}
        icon={<IconHistory stroke={1.5} />}
        actionIcon={{ 'aria-label': 'Callback history' }}
        onClick={onShowHistory}
      />
      <ActionIconWithConfirmation
        tooltip={{ label }}
        icon={
          isDone ? <IconArrowBackUp stroke={1.5} /> : <IconCheck stroke={1.5} />
        }
        actionIcon={{ 'aria-label': label, loading: isBusy, disabled: isBusy }}
        onClick={handleClick}
        confirmButton={{
          label: isDone ? 'Confirm pending' : 'Confirm done',
        }}
      />
    </ActionIconWithConfirmation.Group>
  )
}
