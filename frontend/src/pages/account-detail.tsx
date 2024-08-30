import {
  GetCasesApiArg,
  GetCasesApiResponse,
  useGetCasesQuery,
  useGetUserQuery,
  useGetUsersQuery,
  User,
  UserCreate,
  useUpdateUserMutation,
} from 'api'
import { AccountPermissions } from 'comps/account-permissions'
import { FormField, getFormSchema, getModelChoices } from 'comps/auto-form'
import { CaseListTable } from 'comps/case-table'
import { ErrorBoundary } from 'comps/error-boundary'
import { FIELD_TYPES } from 'comps/field-component'
import { FieldTable, TableForm } from 'comps/table-form'
import { TimelineNote } from 'comps/timeline-item'
import moment from 'moment'
import React, { useState } from 'react'
import {
  Container,
  Header,
  Icon,
  Pagination,
  PaginationProps,
  Tab,
} from 'semantic-ui-react'
import { mount } from 'utils'
import * as Yup from 'yup'

interface DjangoContext {
  user: User
  account_id: number
  is_lawyer_account: boolean
  is_current_user_account: boolean
  performance_notes: any[]
}

const CONTEXT = (window as any).REACT_CONTEXT as DjangoContext

const App = () => {
  const accountResult = useGetUserQuery({ id: CONTEXT.account_id })
  if (accountResult.isLoading) {
    return null
  }
  return <AccountDetailPage data={accountResult.data} />
}

export const AccountDetailPage = ({ data }: { data: User }) => {
  const [account, setAccount] = useState<User>(data)

  const [updateUser] = useUpdateUserMutation()
  const update = (id: string, values: { [fieldName: string]: unknown }) =>
    updateUser({
      id: account.id,
      userCreate: values as UserCreate,
    }).unwrap()

  let tabPanes = [
    {
      menuItem: 'Paralegal cases',
      render: () => <ParalegalCasesTab account={account} />,
    },
    {
      menuItem: 'Lawyer cases',
      render: () => <LawyerCasesTab account={account} />,
    },
    {
      menuItem: 'Performance notes',
      render: () => (
        <Tab.Pane>
          {CONTEXT.performance_notes.length < 1 && 'No notes yet'}
          {CONTEXT.performance_notes.map((note) => (
            <TimelineNote note={note} key={note.id} />
          ))}
        </Tab.Pane>
      ),
    },
    {
      menuItem: 'Permissions',
      render: () => (
        <Tab.Pane>
          <ErrorBoundary>
            <AccountPermissions account={account} setAccount={setAccount} />
          </ErrorBoundary>
        </Tab.Pane>
      ),
    },
  ]

  // Show the lawyer tab first for lawyer accounts and don't display it at all
  // for non-lawyer accounts.
  if (CONTEXT.is_lawyer_account) {
    tabPanes = [tabPanes[1], tabPanes[0], tabPanes[2], tabPanes[3]]
  } else {
    tabPanes = [tabPanes[0], tabPanes[2], tabPanes[3]]
  }

  return (
    <Container>
      <Header as="h1" disabled={!account.is_active}>
        {account.full_name} {!account.is_active && ' (inactive)'}
        <Header.Subheader>{account.email}</Header.Subheader>
      </Header>
      <Header as="h3">User details</Header>

      {CONTEXT.user.is_coordinator_or_better ? (
        <TableForm
          fields={FIELDS}
          schema={SCHEMA}
          model={account}
          setModel={setAccount}
          modelName="account"
          onUpdate={update}
        />
      ) : (
        <FieldTable
          fields={FIELDS}
          model={account}
          choices={getModelChoices(FIELDS, account)}
        />
      )}
      {(CONTEXT.user.is_coordinator_or_better ||
        CONTEXT.is_current_user_account) && (
        <Tab style={{ marginTop: '2em' }} panes={tabPanes} />
      )}
    </Container>
  )
}

export const ParalegalCasesTab = ({ account }: { account: User }) => {
  const [args, setArgs] = useState<GetCasesApiArg>({
    paralegal: account.id.toString(),
  })
  const result = useGetCasesQuery(args)

  const onPageChange = (
    e: React.MouseEvent<HTMLAnchorElement>,
    { activePage }: { activePage?: number | string }
  ) => setArgs({ ...args, page: activePage as number })

  return (
    <Tab.Pane loading={result.isLoading}>
      <PaginatedCaseList
        data={result.data}
        fields={PARALEGAL_TABLE_FIELDS}
        onPageChange={onPageChange}
      />
    </Tab.Pane>
  )
}

export const LawyerCasesTab = ({ account }: { account: User }) => {
  const [args, setArgs] = useState<GetCasesApiArg>({
    lawyer: account.id.toString(),
  })
  const result = useGetCasesQuery(args)

  const onPageChange = (
    e: React.MouseEvent<HTMLAnchorElement>,
    { activePage }: { activePage?: number | string }
  ) => setArgs({ ...args, page: activePage as number })

  return (
    <Tab.Pane loading={result.isLoading}>
      <PaginatedCaseList
        data={result.data}
        fields={LAWYER_TABLE_FIELDS}
        onPageChange={onPageChange}
      />
    </Tab.Pane>
  )
}

export const PaginatedCaseList = ({
  data,
  fields,
  onPageChange,
}: {
  data: GetCasesApiResponse
  fields: string[]
  onPageChange: (
    event: React.MouseEvent<HTMLAnchorElement>,
    data: PaginationProps
  ) => void
}) => {
  if (!data) {
    return null
  }
  const results = [...data.results]
  const currentPage = data.current
  const totalPages = data.page_count
  const itemCount = data.item_count

  return (
    <>
      <CaseListTable issues={results.sort(creationSort)} fields={fields} />
      {itemCount > results.length && (
        <Pagination
          activePage={currentPage}
          onPageChange={onPageChange}
          totalPages={totalPages}
          ellipsisItem={{
            content: <Icon name="ellipsis horizontal" />,
            icon: true,
          }}
          firstItem={{
            content: <Icon name="angle double left" />,
            icon: true,
          }}
          lastItem={{
            content: <Icon name="angle double right" />,
            icon: true,
          }}
          prevItem={{ content: <Icon name="angle left" />, icon: true }}
          nextItem={{ content: <Icon name="angle right" />, icon: true }}
        />
      )}
    </>
  )
}

const creationSort = (a: any, b: any) =>
  moment(b.created_at, 'DD/MM/YY').unix() -
  moment(a.created_at, 'DD/MM/YY').unix()

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
    label: 'Is active?',
    type: FIELD_TYPES.BOOL,
    name: 'is_active',
    schema: Yup.boolean(),
  },
  {
    label: 'Is system account?',
    type: FIELD_TYPES.BOOL,
    name: 'is_system_account',
    schema: Yup.boolean(),
  },
]
const SCHEMA = getFormSchema(FIELDS)

mount(App)
