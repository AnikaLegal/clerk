import {
  Center,
  Group,
  Loader,
  Pagination,
  Switch,
  Table,
  Text,
} from '@mantine/core'
import {
  IconArrowBackUp,
  IconCheck,
  IconPencil,
  IconPhonePlus,
} from '@tabler/icons-react'
import api, {
  Call,
  Contact,
  EnquiryUpdate,
  GetCallsApiArg,
  GetContactsApiArg,
} from 'api'
import { ActionIconWithConfirmation } from 'comps/action-icon'
import { SelectFilter } from 'comps/filter'
import dayjs from 'dayjs'
import { enqueueSnackbar } from 'notistack'
import React, { useEffect, useState } from 'react'
import { ErrorResult, getAPIErrorMessage } from 'utils'
import CommentCell from './comment-cell'
import CommentsModal from './comments-modal'

export type EnquiryKind = 'call' | 'contact'

export interface TopicOption {
  value: string
  label: string
}

const formatTime = (value: string) => dayjs(value).format('DD/MM/YY h:mma')

const NO_WRAP = { whiteSpace: 'nowrap' } as const

const DEFAULT_ARGS = { requiresCallback: true, page: 1 }

type Save = (id: number, update: EnquiryUpdate) => Promise<unknown>

export const CallTable = ({
  topicOptions,
}: {
  topicOptions: TopicOption[]
}) => {
  const [args, setArgs] = useState<GetCallsApiArg>(DEFAULT_ARGS)
  const result = api.useGetCallsQuery(args)
  const [updateCall] = api.useUpdateCallMutation()
  const save: Save = (id, enquiryUpdate) =>
    updateCall({ id, enquiryUpdate }).unwrap()

  return (
    <EnquiryTable<Call>
      args={args}
      setArgs={setArgs}
      result={result}
      save={save}
      topicOptions={topicOptions}
      headers={['Received', 'Phone number', 'Topic']}
      cells={(call) => [
        formatTime(call.created_at),
        call.phone_number,
        call.topic_display,
      ]}
      modalSubtitle={(call) =>
        `${call.phone_number} · Received ${formatTime(call.created_at)} · ${call.topic_display}`
      }
    />
  )
}

export const ContactTable = () => {
  const [args, setArgs] = useState<GetContactsApiArg>(DEFAULT_ARGS)
  const result = api.useGetContactsQuery(args)
  const [updateContact] = api.useUpdateContactMutation()
  const save: Save = (id, enquiryUpdate) =>
    updateContact({ id, enquiryUpdate }).unwrap()

  return (
    <EnquiryTable<Contact>
      args={args}
      setArgs={setArgs}
      result={result}
      save={save}
      headers={['Received', 'Name', 'Email', 'Phone number', 'Referral']}
      cells={(contact) => [
        formatTime(contact.created_at),
        contact.name,
        contact.email,
        contact.phone,
        contact.referral,
      ]}
      modalSubtitle={(contact) =>
        `${contact.name} · Received ${formatTime(contact.created_at)}`
      }
    />
  )
}

interface ListArgs {
  requiresCallback?: boolean
  topic?: string
  page?: number
}

interface ListResult<T> {
  data?: { results: T[]; page_count: number }
  isLoading: boolean
  isError: boolean
  error?: unknown
}

interface EnquiryTableProps<T extends Call | Contact> {
  args: ListArgs
  setArgs: React.Dispatch<React.SetStateAction<ListArgs>>
  result: ListResult<T>
  save: Save
  topicOptions?: TopicOption[]
  headers: string[]
  cells: (record: T) => React.ReactNode[]
  modalSubtitle: (record: T) => string
}

const EnquiryTable = <T extends Call | Contact>({
  args,
  setArgs,
  result,
  save,
  topicOptions,
  headers,
  cells,
  modalSubtitle,
}: EnquiryTableProps<T>) => {
  const [editing, setEditing] = useState<T | null>(null)
  const page = args.page || 1
  const columnCount = headers.length + 4

  const results = result.data?.results

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

  const saveWithMessage = (id: number, update: EnquiryUpdate, ok: string) =>
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
      <Group justify="space-between" align="flex-end" mt="md">
        <Switch
          label="Show done"
          size="md"
          checked={args.requiresCallback === undefined}
          onChange={(e) =>
            handleFilterChange(
              'requiresCallback',
              e.currentTarget.checked ? undefined : true
            )
          }
        />
        {topicOptions && (
          <SelectFilter
            name="topic"
            label="Topic"
            placeholder="Any"
            w={260}
            data={topicOptions}
            value={args.topic ?? null}
            onFilterChange={handleFilterChange}
          />
        )}
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
            {headers.map((header) => (
              <Table.Th key={header}>{header}</Table.Th>
            ))}
            <Table.Th>Callbacks</Table.Th>
            <Table.Th>Comments</Table.Th>
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
                    style={i === 0 ? NO_WRAP : undefined}
                  >
                    {cell}
                  </Table.Td>
                ))}
                <Table.Td>{record.number_callbacks}</Table.Td>
                <Table.Td>
                  <CommentCell
                    comments={record.comments}
                    onSave={(comments) =>
                      saveWithMessage(
                        record.id,
                        { comments },
                        'Enquiry updated'
                      )
                    }
                  />
                </Table.Td>
                <Table.Td style={NO_WRAP}>
                  {formatTime(record.modified_at)}
                </Table.Td>
                <Table.Td>
                  <RowActions
                    record={record}
                    save={saveWithMessage}
                    onComments={() => setEditing(record)}
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
      {editing && (
        <CommentsModal
          opened
          record={editing}
          subtitle={modalSubtitle(editing)}
          onClose={() => setEditing(null)}
          onSave={(update) =>
            saveWithMessage(editing.id, update, 'Enquiry updated')
          }
        />
      )}
    </>
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
  save: (id: number, update: EnquiryUpdate, ok: string) => Promise<unknown>
  onComments: () => void
}

const RowActions = ({ record, save, onComments }: RowActionsProps) => {
  const [busy, setBusy] = useState<'attempt' | 'done' | null>(null)
  const isDone = !record.requires_callback

  // The icons stay disabled until the refreshed row arrives, so a second
  // click can't resend a count the list hasn't caught up with.
  useEffect(() => setBusy(null), [record.modified_at])

  const run = (
    action: 'attempt' | 'done',
    update: EnquiryUpdate,
    ok: string
  ) => {
    setBusy(action)
    save(record.id, update, ok).catch(() => setBusy(null))
  }

  return (
    <ActionIconWithConfirmation.Group>
      <ActionIconWithConfirmation
        tooltip={{ label: 'Log a callback attempt' }}
        icon={<IconPhonePlus stroke={1.5} />}
        actionIcon={{
          'aria-label': 'Log a callback attempt',
          loading: busy === 'attempt',
          disabled: busy !== null,
        }}
        onClick={() =>
          run(
            'attempt',
            { number_callbacks: record.number_callbacks + 1 },
            'Attempt logged'
          )
        }
      />
      <ActionIconWithConfirmation
        tooltip={{ label: 'Update enquiry' }}
        icon={<IconPencil stroke={1.5} />}
        actionIcon={{ 'aria-label': 'Update enquiry', disabled: busy !== null }}
        onClick={onComments}
      />
      <ActionIconWithConfirmation
        tooltip={{ label: isDone ? 'Mark pending' : 'Mark done' }}
        icon={
          isDone ? <IconArrowBackUp stroke={1.5} /> : <IconCheck stroke={1.5} />
        }
        actionIcon={{
          'aria-label': isDone ? 'Mark pending' : 'Mark done',
          loading: busy === 'done',
          disabled: busy !== null,
        }}
        onClick={() =>
          run(
            'done',
            { requires_callback: isDone },
            isDone ? 'Marked pending' : 'Marked done'
          )
        }
        confirmButton={{
          label: isDone ? 'Confirm pending' : 'Confirm done',
        }}
      />
    </ActionIconWithConfirmation.Group>
  )
}
