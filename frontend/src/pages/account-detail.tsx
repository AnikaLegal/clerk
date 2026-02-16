import {
  Center,
  Container,
  Group,
  Loader,
  Pagination,
  Tabs,
  TabsPanelProps,
  Text,
  Title,
} from '@mantine/core'
import { IconExclamationCircle } from '@tabler/icons-react'
import {
  GetCasesApiArg,
  GetNotesApiArg,
  useGetCasesQuery,
  useGetNotesQuery,
  useGetUserQuery,
  User,
  UserCreate,
  useUpdateUserMutation,
} from 'api'
import { MicrosoftAccountAccess } from 'comps/microsoft-account-access'
import { FormField, getFormSchema } from 'comps/auto-form'
import { CaseListTable } from 'comps/case-table'
import { ErrorBoundary } from 'comps/error-boundary'
import { FIELD_TYPES } from 'comps/field-component'
import { showNotification } from 'comps/notification'
import { TableForm } from 'comps/table-form'
import { TimelineNote } from 'comps/timeline-item'
import React, { useEffect, useState } from 'react'
import { getAPIErrorMessage, mount } from 'utils'
import * as Yup from 'yup'

interface DjangoContext {
  user: User
  account_id: number
}

const CONTEXT = (window as any).REACT_CONTEXT as DjangoContext

const App = () => {
  const result = useGetUserQuery({ id: CONTEXT.account_id })

  if (result.isError) {
    return (
      <ErrorState error={result.error} title="Could not load account details" />
    )
  }
  if (result.isLoading) {
    return (
      <Center>
        <Loader size="lg" />
      </Center>
    )
  }
  return (
    <Container size="xl">
      <AccountDetailHeader result={result} />
      <AccountUserDetails result={result} />
      <AccountTabs result={result} />
    </Container>
  )
}

interface AccountDetailHeaderProps {
  result: ReturnType<typeof useGetUserQuery>
}

const AccountDetailHeader = ({ result }: AccountDetailHeaderProps) => {
  const isActive = result.data?.is_active
  return (
    <>
      <Title order={1} c={isActive ? 'inherit' : 'dimmed'}>
        {result.data?.full_name} {!isActive && ' (inactive)'}
      </Title>
      <Text c="dimmed">{result.data?.email}</Text>
    </>
  )
}

interface AccountUserDetailsProps {
  result: ReturnType<typeof useGetUserQuery>
}

const AccountUserDetails = ({ result }: AccountUserDetailsProps) => {
  const [account, setAccount] = useState<User>(result.data)
  const [updateUser] = useUpdateUserMutation()

  const update = (id: string, values: { [fieldName: string]: unknown }) =>
    updateUser({
      id: account.id,
      userCreate: values as UserCreate,
    }).unwrap()

  return (
    <>
      <Title order={3} mt="lg">
        User details
      </Title>
      <TableForm
        fields={FIELDS}
        schema={SCHEMA}
        model={account}
        setModel={setAccount}
        modelName="account"
        onUpdate={update}
      />
    </>
  )
}

interface AccountTabsProps {
  result: ReturnType<typeof useGetUserQuery>
}

const enum ACCOUNT_TABS {
  PARALEGAL = 'paralegal',
  LAWYER = 'lawyer',
  NOTES = 'notes',
  PERMISSIONS = 'permissions',
}

const AccountTabs = ({ result }: AccountTabsProps) => {
  const [activeTab, setActiveTab] = useState<string | null>(null)

  return (
    <Tabs
      variant="outline"
      mt="xl"
      onChange={setActiveTab}
      defaultValue={ACCOUNT_TABS.PARALEGAL}
      keepMounted={false}
    >
      <Tabs.List>
        <Tabs.Tab value={ACCOUNT_TABS.PARALEGAL}>
          <Text fw={activeTab === ACCOUNT_TABS.PARALEGAL ? 'bold' : 'normal'}>
            Paralegal cases
          </Text>
        </Tabs.Tab>
        <Tabs.Tab value={ACCOUNT_TABS.LAWYER}>
          <Text fw={activeTab === ACCOUNT_TABS.LAWYER ? 'bold' : 'normal'}>
            Lawyer cases
          </Text>
        </Tabs.Tab>
        <Tabs.Tab value={ACCOUNT_TABS.NOTES}>
          <Text fw={activeTab === ACCOUNT_TABS.NOTES ? 'bold' : 'normal'}>
            Performance notes
          </Text>
        </Tabs.Tab>
        <Tabs.Tab value={ACCOUNT_TABS.PERMISSIONS}>
          <Text fw={activeTab === ACCOUNT_TABS.PERMISSIONS ? 'bold' : 'normal'}>
            Microsoft account
          </Text>
        </Tabs.Tab>
      </Tabs.List>
      <ParalegalTabsPanel
        account={result.data}
        value={ACCOUNT_TABS.PARALEGAL}
        p="sm"
      />
      <LawyerTabsPanel
        account={result.data}
        value={ACCOUNT_TABS.LAWYER}
        p="sm"
      />
      <NotesTabsPanel account={result.data} value={ACCOUNT_TABS.NOTES} p="sm" />
      <MicrosoftAccountAccessTabsPanel
        account={result.data}
        value={ACCOUNT_TABS.PERMISSIONS}
        p="sm"
      />
    </Tabs>
  )
}

interface AccountTabsPanelProps extends Omit<TabsPanelProps, 'children'> {
  account: User
}

const ParalegalTabsPanel = ({ account, ...props }: AccountTabsPanelProps) => {
  const [args, setArgs] = useState<GetCasesApiArg>({
    paralegal: account.id.toString(),
  })
  const result = useGetCasesQuery(args)
  const onPageChange = (page) => setArgs({ ...args, page })

  return (
    <TabPanelWithBorder {...props}>
      <PaginatedCaseList
        result={result}
        fields={PARALEGAL_TABLE_FIELDS}
        onPageChange={onPageChange}
      />
    </TabPanelWithBorder>
  )
}

const LawyerTabsPanel = ({ account, ...props }: AccountTabsPanelProps) => {
  const [args, setArgs] = useState<GetCasesApiArg>({
    lawyer: account.id.toString(),
  })
  const result = useGetCasesQuery(args)
  const onPageChange = (page) => setArgs({ ...args, page })

  return (
    <TabPanelWithBorder {...props}>
      <PaginatedCaseList
        result={result}
        fields={LAWYER_TABLE_FIELDS}
        onPageChange={onPageChange}
      />
    </TabPanelWithBorder>
  )
}

const NotesTabsPanel = ({ account, ...props }: AccountTabsPanelProps) => {
  const [args, setArgs] = useState<GetNotesApiArg>({
    reviewee: account.id,
    pageSize: 5,
  })
  const result = useGetNotesQuery(args)
  const onPageChange = (page) => setArgs({ ...args, page })

  return (
    <TabPanelWithBorder {...props}>
      <PaginatedNotesList result={result} onPageChange={onPageChange} />
    </TabPanelWithBorder>
  )
}

const MicrosoftAccountAccessTabsPanel = ({
  account,
  ...props
}: AccountTabsPanelProps) => {
  return (
    <TabPanelWithBorder {...props}>
      <ErrorBoundary>
        <MicrosoftAccountAccess account={account} />
      </ErrorBoundary>
    </TabPanelWithBorder>
  )
}

interface TabsPanelWithBorderProps extends TabsPanelProps {
  children: React.ReactNode
}

const TabPanelWithBorder = ({
  children,
  ...props
}: TabsPanelWithBorderProps) => {
  const border =
    'calc(0.0625rem * var(--mantine-scale)) solid var(--tab-border-color)'
  return (
    <Tabs.Panel
      {...props}
      style={{
        borderLeft: border,
        borderRight: border,
        borderBottom: border,
      }}
    >
      {children}
    </Tabs.Panel>
  )
}

interface ErrorStateProps {
  title: string
  error: any
}

const ErrorState = ({ error, title }: ErrorStateProps) => {
  useEffect(() => {
    const message = getAPIErrorMessage(error)
    showNotification({ type: 'error', title: title, message: message })
  }, [error])

  return (
    <Group justify="center" gap="xs" m="sm" c="red">
      <IconExclamationCircle />
      <Text>{title}</Text>
    </Group>
  )
}

interface PaginatedCaseListProps {
  result: ReturnType<typeof useGetCasesQuery>
  fields: string[]
  onPageChange: (value: number) => void
}

export const PaginatedCaseList = ({
  result,
  fields,
  onPageChange,
}: PaginatedCaseListProps) => {
  if (result.isError) {
    return <ErrorState error={result.error} title="Could not load cases" />
  }

  if (result.isLoading) {
    return (
      <Center>
        <Loader size="lg" />
      </Center>
    )
  }
  return (
    <>
      <CaseListTable issues={result.data.results} fields={fields} />
      {!result.isLoading && result.data && (
        <Pagination
          value={result.data.current}
          total={result.data.page_count}
          onChange={onPageChange}
          mt="md"
          withEdges
          withControls
        />
      )}
    </>
  )
}

interface PaginatedNotesListProps {
  result: ReturnType<typeof useGetNotesQuery>
  onPageChange: (value: number) => void
}

export const PaginatedNotesList = ({
  result,
  onPageChange,
}: PaginatedNotesListProps) => {
  if (result.isError) {
    return <ErrorState error={result.error} title="Could not load notes" />
  }

  if (result.isLoading) {
    return (
      <Center>
        <Loader size="lg" />
      </Center>
    )
  }

  return (
    <>
      {result.data.item_count == 0
        ? 'No notes yet'
        : result.data.results.map((note) => (
            <TimelineNote note={note} key={note.id} />
          ))}
      {!result.isLoading && result.data && result.data.item_count > 0 && (
        <Pagination
          value={result.data.current}
          total={result.data.page_count}
          onChange={onPageChange}
          mt="md"
          withEdges
          withControls
        />
      )}
    </>
  )
}

const PARALEGAL_TABLE_FIELDS = [
  'fileref',
  'topic',
  'client',
  'lawyer',
  'created_at',
  'stage',
  'provided_legal_services',
  'outcome',
]
const LAWYER_TABLE_FIELDS = [
  'fileref',
  'topic',
  'client',
  'paralegal',
  'created_at',
  'stage',
  'provided_legal_services',
  'outcome',
]

const FIELDS: FormField[] = [
  {
    label: 'First name',
    schema: Yup.string().required('Required'),
    type: FIELD_TYPES.TEXT,
    name: 'first_name',
  },
  {
    label: 'Last name',
    schema: Yup.string().required('Required'),
    type: FIELD_TYPES.TEXT,
    name: 'last_name',
  },
  {
    label: 'Is intern?',
    name: 'is_intern',
    type: FIELD_TYPES.BOOL,
    schema: Yup.string().required('Required'),
  },
  {
    label: 'Case capacity',
    type: FIELD_TYPES.TEXT,
    name: 'case_capacity',
    schema: Yup.number().integer().min(0),
  },
  {
    label: 'Groups',
    type: FIELD_TYPES.MULTI_CHOICE,
    name: 'groups',
    schema: Yup.array().of(Yup.string()),
  },
  {
    label: 'Is active?',
    type: FIELD_TYPES.BOOL,
    name: 'is_active',
    schema: Yup.boolean(),
  },
]
const SCHEMA = getFormSchema(FIELDS)

mount(App)
