import {
  Button,
  Center,
  Container,
  Group,
  Pagination,
  Table,
  Text,
  Title,
} from '@mantine/core'
import { useDisclosure } from '@mantine/hooks'
import api, {
  GetCaseDatesApiArg,
  Issue,
  IssueDate,
  IssueDateCreate,
  useCreateCaseDateMutation,
} from 'api'
import { CASE_TABS, CaseHeader, CaseTabUrls } from 'comps/case-header'
import {
  DateActionIconGroup,
  DateFormControlProps,
  DateFormModal,
  DateFormType,
  DateTable,
  DateTableDateCell,
  DateTableHearingLocationCell,
  DateTableHearingTypeCell,
  DateTableIsReviewedCell,
  DateTableNotesCell,
  DateTableTypeCell,
} from 'features/date'
import { enqueueSnackbar } from 'notistack'
import React, { useState } from 'react'
import { UserPermission } from 'types'
import { getAPIErrorMessage, getAPIFormErrors, mount } from 'utils'

interface DjangoContext {
  case_pk: string
  urls: CaseTabUrls
  user: UserPermission
}
const CONTEXT = (window as any).REACT_CONTEXT as DjangoContext

const App = () => {
  const caseId = CONTEXT.case_pk
  const urls = CONTEXT.urls

  const result = api.useGetCaseQuery({ id: caseId })
  if (result.isFetching || !result.data) {
    return null
  }
  const issue = result.data.issue

  return (
    <Container size="xl">
      <CaseHeader issue={issue} activeTab={CASE_TABS.DATES} urls={urls} />
      <CaseDateHeader issue={issue} />
      <CaseDateTable issue={issue} />
    </Container>
  )
}

interface CaseDateHeaderProps {
  issue: Issue
}

const CaseDateHeader = ({ issue }: CaseDateHeaderProps) => {
  const [isOpen, handler] = useDisclosure(false)
  const [createDate] = useCreateCaseDateMutation()

  const initialValues: IssueDateCreate = {
    type: undefined!,
    date: undefined!,
    issue_id: issue.id,
  }

  const handleSubmit = (form: DateFormType, values: IssueDateCreate) => {
    form.setSubmitting(true)
    createDate({
      issueDateCreate: values,
    })
      .unwrap()
      .then((date) => {
        enqueueSnackbar('Critical date created', { variant: 'success' })
        handler.close()
      })
      .catch((e) => {
        enqueueSnackbar(
          getAPIErrorMessage(e, 'Failed to create critical date'),
          {
            variant: 'error',
          }
        )
        const requestErrors = getAPIFormErrors(e)
        if (requestErrors) {
          form.setErrors(requestErrors)
        }
      })
      .finally(() => {
        form.setSubmitting(false)
      })
  }

  return (
    <>
      <Title order={2} mt="xl">
        <Group wrap="nowrap" gap="sm" justify="space-between">
          <span>Critical Dates</span>
          <Button onClick={() => handler.open()}>
            Create a new critical date
          </Button>
        </Group>
      </Title>
      <DateFormModal
        input={{
          initialValues: initialValues,
        }}
        modal={{
          opened: isOpen,
          title: 'Create a new critical date',
        }}
        onSubmit={handleSubmit}
        onCancel={() => handler.close()}
        controls={ModalDateFormControls}
      />
    </>
  )
}

const ModalDateFormControls = ({ form, onCancel }: DateFormControlProps) => {
  return (
    <Group justify="right" mt="lg">
      <Button
        variant="default"
        onClick={onCancel}
        disabled={form.submitting}
        size="md"
      >
        Close
      </Button>
      <Button
        type="submit"
        disabled={form.submitting}
        loading={form.submitting}
        size="md"
      >
        Create critical date
      </Button>
    </Group>
  )
}

interface CaseDateTableProps {
  issue: Issue
}

const CaseDateTable = ({ issue }: CaseDateTableProps) => {
  const [args, setArgs] = useState<GetCaseDatesApiArg>({
    issueId: issue.id,
    page: 1,
  })
  const result = api.useGetCaseDatesQuery(args)

  const headerRow = (
    <Table.Tr>
      <Table.Th>Date</Table.Th>
      <Table.Th>Type</Table.Th>
      <Table.Th>Hearing type</Table.Th>
      <Table.Th>Hearing location</Table.Th>
      <Table.Th>Notes</Table.Th>
      <Table.Th>Reviewed?</Table.Th>
      <Table.Th></Table.Th>
    </Table.Tr>
  )

  return (
    <>
      {!result.isLoading && result.data && (
        <Text c="dimmed">
          Showing {result.data.results.length} of {result.data.item_count}{' '}
          critical dates
        </Text>
      )}
      <DateTable
        result={result}
        headerRow={headerRow}
        dataRow={DateTableDataRow}
      />
      {!result.isLoading && result.data && (
        <Pagination
          total={result.data.page_count}
          value={args.page || 1}
          onChange={(page) => setArgs({ ...args, page })}
          mt="md"
          withEdges
          withControls
        />
      )}
    </>
  )
}

const DateTableDataRow = ({ date }: { date: IssueDate }) => {
  return (
    <Table.Tr>
      <DateTableDateCell date={date} />
      <DateTableTypeCell date={date} />
      <DateTableHearingTypeCell date={date} />
      <DateTableHearingLocationCell date={date} />
      <DateTableNotesCell date={date} />
      <DateTableIsReviewedCell date={date} />
      <Table.Td>
        <Center>
          <DateActionIconGroup date={date} user={CONTEXT.user} />
        </Center>
      </Table.Td>
    </Table.Tr>
  )
}

mount(App)
