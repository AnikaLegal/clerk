import {
  GetCasesApiArg,
  GetCasesApiResponse,
  GetNotesApiArg,
  GetNotesApiResponse,
  useGetCasesQuery,
  useGetNotesQuery,
  useGetUserQuery,
  User,
  UserCreate,
  useUpdateUserMutation,
} from 'api'
import { AccountPermissions } from 'comps/account-permissions'
import { FormField, getFormSchema, getModelChoices } from 'comps/auto-form'
import { CaseListTable } from 'comps/case-table'
import { ErrorBoundary } from 'comps/error-boundary'
import { ErrorMessage } from 'comps/error-message'
import { FIELD_TYPES } from 'comps/field-component'
import { FieldTable, TableForm } from 'comps/table-form'
import { TimelineNote } from 'comps/timeline-item'
import moment from 'moment'
import React, { useState } from 'react'
import {
  Container,
  Header,
  Icon,
  Loader,
  Pagination,
  PaginationProps,
  Tab,
  Grid,
  Segment,
} from 'semantic-ui-react'
import { mount } from 'utils'
import * as Yup from 'yup'

interface DjangoContext {
  user: User
  account_id: number
  current_user_id: number
}

const CONTEXT = (window as any).REACT_CONTEXT as DjangoContext

const App = () => {
  const result = useGetUserQuery({ id: CONTEXT.account_id })
  if (result.isLoading) {
    return (
      <Loader active inline="centered" />
    )
  }
  if (result.isError) {
    return (
      <Grid centered>
        <Segment basic>
          <ErrorMessage error={result.error} />
        </Segment>
      </Grid>
    )
  }
  if (!result.data) {
    return null
  }
  return <AccountDetailPage data={result.data} />
}

export const AccountDetailPage = ({ data }: { data: User }) => {
  const [account, setAccount] = useState<User>(data)
  const [updateUser] = useUpdateUserMutation()

  const update = (id: string, values: { [fieldName: string]: unknown }) =>
    updateUser({
      id: account.id,
      userCreate: values as UserCreate,
    }).unwrap()

  const showTabs =
    CONTEXT.user.is_coordinator_or_better ||
    CONTEXT.account_id === CONTEXT.current_user_id

  interface pane {
    menuItem?: any
    render?: () => React.ReactNode
  }
  let tabPanes: pane[] = []

  if (showTabs) {
    // Show the lawyer tab for lawyer accounts only.
    if (account.is_lawyer) {
      tabPanes.push({
        menuItem: 'Lawyer cases',
        render: () => <LawyerCasesTab account={account} />,
      })
    }

    tabPanes.push({
      menuItem: 'Paralegal cases',
      render: () => <ParalegalCasesTab account={account} />,
    })

    if (CONTEXT.user.is_coordinator_or_better) {
      tabPanes.push({
        menuItem: 'Performance notes',
        render: () => <PerformanceNotesTab account={account} />,
      })
    }

    tabPanes.push({
      menuItem: 'Permissions',
      render: () => (
        <Tab.Pane>
          <ErrorBoundary>
            <AccountPermissions account={account} setAccount={setAccount} />
          </ErrorBoundary>
        </Tab.Pane>
      ),
    })
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
      {showTabs && <Tab style={{ marginTop: '2em' }} panes={tabPanes} />}
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

export const PerformanceNotesTab = ({ account }: { account: User }) => {
  const [args, setArgs] = useState<GetNotesApiArg>({
    noteType: 'PERFORMANCE',
    reviewee: account.id.toString(),
  })
  const result = useGetNotesQuery(args)
  const onPageChange = (
    e: React.MouseEvent<HTMLAnchorElement>,
    { activePage }: { activePage?: number | string }
  ) => setArgs({ ...args, page: activePage as number })

  return (
    <Tab.Pane loading={result.isLoading}>
      <PaginatedNotes data={result.data} onPageChange={onPageChange} />
    </Tab.Pane>
  )
}

export const PaginatedCaseList = ({
  data,
  fields,
  onPageChange,
}: {
  data: GetCasesApiResponse | undefined
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

export const PaginatedNotes = ({
  data,
  onPageChange,
}: {
  data: GetNotesApiResponse | undefined
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
      {results.length == 0
        ? 'No notes yet'
        : results.map((note) => <TimelineNote note={note} key={note.id} />)}
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
]
const SCHEMA = getFormSchema(FIELDS)

mount(App)
