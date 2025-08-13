import {
  ActionIcon,
  Button,
  Center,
  Container,
  Grid,
  Group,
  Loader,
  MantineColor,
  Pagination,
  Select,
  SelectProps,
  Table,
  Text,
  TextInput,
  TextInputProps,
  Title,
  Tooltip,
} from '@mantine/core'
import {
  useClickOutside,
  useDebouncedCallback,
  useDisclosure,
  UseDisclosureHandlers,
} from '@mantine/hooks'
import {
  IconCheck,
  IconExclamationCircle,
  IconPencil,
  IconTrash,
  IconX,
} from '@tabler/icons-react'
import api, {
  GetCaseDatesApiArg,
  IssueDate,
  IssueDateCreate,
  useDeleteCaseDateMutation,
  useGetCaseDatesQuery,
  useUpdateCaseDateMutation,
} from 'api'
import { CaseDateFormModal } from 'comps/modal'
import { RichTextDisplay } from 'comps/rich-text'
import dayjs from 'dayjs'
import customParseFormat from 'dayjs/plugin/customParseFormat'
import { useCaseDateForm } from 'forms/case-date'
import { enqueueSnackbar } from 'notistack'
import React, { useEffect, useState } from 'react'
import { UserPermission } from 'types'
import { choiceToMap, getAPIErrorMessage, mount } from 'utils'

dayjs.extend(customParseFormat)

import '@mantine/core/styles.css'

interface DjangoContext {
  choices: {
    type: [string, string][]
  }
  user: UserPermission
}
const CONTEXT = (window as any).REACT_CONTEXT as DjangoContext
const Types = CONTEXT.choices.type.sort((a, b) => a[1].localeCompare(b[1]))
const TypeLabels = choiceToMap(Types)

const App = () => {
  const [args, setArgs] = useState<GetCaseDatesApiArg>({
    isReviewed: false,
    page: 1,
  })
  const result = api.useGetCaseDatesQuery(args)

  const handleFilterChange = (key: keyof GetCaseDatesApiArg, value: any) => {
    setArgs((prevArgs) => ({
      ...prevArgs,
      [key]: value !== null ? value : undefined,
      page: 1, // Reset to first page on filter change
    }))
  }

  return (
    <Container size="xl">
      <Title order={1}>Critical Dates</Title>
      {!result.isLoading && result.data && (
        <Text c="dimmed">
          Showing {result.data.results.length} of {result.data.item_count}{' '}
          critical dates
        </Text>
      )}
      <Grid mt="lg">
        <Grid.Col span={12}>
          <TextInputFilter
            name="q"
            label="Search"
            placeholder="Search by client name, email, or file ref"
            onFilterChange={handleFilterChange}
          />
        </Grid.Col>
        <Grid.Col span={6}>
          <SelectFilter
            name="type"
            data={Types.map((type) => ({
              value: type[0],
              label: type[1],
            }))}
            label="Date type"
            value={args.type || ''}
            onFilterChange={handleFilterChange}
          />
        </Grid.Col>
        <Grid.Col span={6}>
          <SelectFilter
            name="isReviewed"
            data={[
              { value: 'true', label: 'Yes' },
              { value: 'false', label: 'No' },
            ]}
            label="Reviewed?"
            value={args.isReviewed?.toString() || ''}
            onFilterChange={handleFilterChange}
          />
        </Grid.Col>
      </Grid>
      <Table
        withColumnBorders
        withTableBorder
        verticalSpacing="md"
        fz="md"
        mt="lg"
      >
        <Table.Thead>
          <Table.Tr>
            <Table.Th>Fileref</Table.Th>
            <Table.Th>Type</Table.Th>
            <Table.Th>Critical date</Table.Th>
            <Table.Th>Client</Table.Th>
            <Table.Th>Notes</Table.Th>
            <Table.Th>Reviewed?</Table.Th>
            <Table.Th></Table.Th>
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>
          <CriticalDatesTableBody result={result} />
        </Table.Tbody>
      </Table>
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
    </Container>
  )
}

interface TextInputFilterProps extends TextInputProps {
  name: keyof GetCaseDatesApiArg
  onFilterChange: (key: keyof GetCaseDatesApiArg, value: any) => void
  isLoading?: boolean
}

const TextInputFilter = ({
  name,
  onFilterChange,
  isLoading = false,
  ...props
}: TextInputFilterProps) => {
  const debouncedFilterChange = useDebouncedCallback(
    (key: keyof GetCaseDatesApiArg, value: any) => {
      onFilterChange(key, value)
    },
    300 // Adjust the debounce delay as needed
  )

  return (
    <TextInput
      size="md"
      value={props.value}
      onChange={(event) =>
        debouncedFilterChange(name, event.currentTarget.value)
      }
      rightSection={isLoading ? <Loader size="sm" /> : null}
      {...props}
    />
  )
}

interface SelectFilterProps extends SelectProps {
  name: keyof GetCaseDatesApiArg
  onFilterChange: (key: keyof GetCaseDatesApiArg, value: any) => void
  isLoading?: boolean
}

const SelectFilter = ({
  name,
  onFilterChange,
  isLoading = false,
  ...props
}: SelectFilterProps) => {
  return (
    <Select
      clearable
      size="md"
      withCheckIcon={false}
      onChange={(value) => onFilterChange(name, value)}
      rightSection={isLoading ? <Loader size="sm" /> : null}
      {...props}
    />
  )
}

const ErrorState = ({ error }: { error: any }) => {
  useEffect(() => {
    const message = getAPIErrorMessage(error, 'Could not load critical dates')
    enqueueSnackbar(message, { variant: 'error' })
  }, [error])

  return (
    <Table.Tr>
      <td colSpan={5}>
        <Group justify="center" gap="xs" m="sm" c="red">
          <IconExclamationCircle />
          <Text>Could not load critical dates</Text>
        </Group>
      </td>
    </Table.Tr>
  )
}

const LoadingState = () => (
  <Table.Tr>
    <td colSpan={5}>
      <Center m="sm">
        <Loader />
      </Center>
    </td>
  </Table.Tr>
)

const EmptyState = () => (
  <Table.Tr>
    <td colSpan={5}>
      <Center m="sm">No dates found</Center>
    </td>
  </Table.Tr>
)

const getDateBackgroundColor = (dateString: string): MantineColor => {
  const date = dayjs(dateString, 'DD/MM/YYYY')
  const now = dayjs()
  if (date.isBefore(now.add(7 + 1, 'day'), 'day')) {
    return 'red.2'
  }
  if (date.isBefore(now.add(14 + 1, 'day'), 'day')) {
    return 'yellow.2'
  }
  return 'green.2'
}

interface CriticalDatesTableBodyProps {
  result: ReturnType<typeof useGetCaseDatesQuery>
}

const CriticalDatesTableBody = ({ result }: CriticalDatesTableBodyProps) => {
  if (result.isError) {
    return <ErrorState error={result.error} />
  }
  if (result.isLoading) {
    return <LoadingState />
  }

  const data: IssueDate[] = result.data.results || []
  if (data.length < 1) {
    return <EmptyState />
  }

  return (
    <>
      {data.map((date) => (
        <Table.Tr key={date.id}>
          <Table.Td>
            <a href={date.issue.url}>{date.issue.fileref}</a>
          </Table.Td>
          <Table.Td>{TypeLabels.get(date.type)}</Table.Td>
          <Table.Td bg={getDateBackgroundColor(date.date)}>
            {date.date}
          </Table.Td>
          <Table.Td>
            <a href={date.issue.client.url}>{date.issue.client.full_name}</a>
          </Table.Td>
          <Table.Td>
            <RichTextDisplay content={date.notes} />
          </Table.Td>
          <Table.Td>
            <Center>
              {date.is_reviewed ? (
                <IconCheck color="var(--mantine-color-green-6)" stroke={3} />
              ) : (
                <IconX color="var(--mantine-color-yellow-6)" stroke={3} />
              )}
            </Center>
          </Table.Td>
          <Table.Td>
            <CriticalDateActionIcons date={date} />
          </Table.Td>
        </Table.Tr>
      ))}
    </>
  )
}

interface CriticalDateActionIconsProps {
  date: IssueDate
}

const CriticalDateActionIcons = ({ date }: CriticalDateActionIconsProps) => {
  const [deleteCaseDate] = useDeleteCaseDateMutation()
  const [updateCaseDate] = useUpdateCaseDateMutation()

  const [displayConfirmReviewed, confirmReviewedHandlers] = useDisclosure(false)
  const [displayEdit, displayEditHandlers] = useDisclosure(false)
  const [displayConfirmDelete, confirmDeleteHandlers] = useDisclosure(false)

  const initialValues: IssueDateCreate = {
    is_reviewed: date.is_reviewed,
    issue_id: date.issue.id,
    type: date.type,
    date: dayjs(date.date, 'DD/MM/YYYY').format('YYYY-MM-DD'),
    notes: date.notes,
  }

  const handleDelete = () => {
    deleteCaseDate({ id: date.id })
      .unwrap()
      .then(() => {
        enqueueSnackbar('Critical date deleted', { variant: 'success' })
      })
      .catch((e) => {
        enqueueSnackbar(
          getAPIErrorMessage(e, 'Failed to delete critical date'),
          {
            variant: 'error',
          }
        )
      })
  }

  const handleReviewed = () => {
    updateCaseDate({
      id: date.id,
      issueDateCreate: {
        ...initialValues,
        is_reviewed: !initialValues.is_reviewed,
      },
    })
      .unwrap()
      .then(() => {
        enqueueSnackbar('Critical date updated', { variant: 'success' })
      })
      .catch((e) => {
        enqueueSnackbar(
          getAPIErrorMessage(e, 'Failed to update critical date'),
          {
            variant: 'error',
          }
        )
      })
      .finally(() => {
        confirmReviewedHandlers.close()
      })
  }

  const handleUpdate = (
    form: ReturnType<typeof useCaseDateForm>,
    values: IssueDateCreate
  ) => {
    form.setSubmitting(true)
    updateCaseDate({
      id: date.id,
      issueDateCreate: values,
    })
      .unwrap()
      .then(() => {
        enqueueSnackbar('Critical date updated', { variant: 'success' })
        displayEditHandlers.close()
      })
      .catch((e) => {
        enqueueSnackbar(
          getAPIErrorMessage(e, 'Failed to update critical date'),
          {
            variant: 'error',
          }
        )
      })
      .finally(() => {
        form.setSubmitting(false)
        form.setValues({})
      })
  }

  if (displayConfirmDelete) {
    return (
      <ActionConfirmation
        onConfirm={handleDelete}
        confirmHandler={confirmDeleteHandlers}
        label="Confirm delete"
        color="red"
      />
    )
  }
  if (displayConfirmReviewed) {
    return (
      <ActionConfirmation
        onConfirm={handleReviewed}
        confirmHandler={confirmReviewedHandlers}
        label={date.is_reviewed ? 'Confirm not reviewed' : 'Confirm reviewed'}
      />
    )
  }

  return (
    <>
      <CaseDateFormModal
        opened={displayEdit}
        onClose={() => displayEditHandlers.close()}
        initialValues={initialValues}
        title="Update critical date"
        submitButtonLabel="Update critical date"
        onFormSubmit={handleUpdate}
      />
      <Center>
        <ActionIcon.Group>
          <ActionIcon variant="transparent" color="gray">
            <Tooltip label="Toggle reviewed" openDelay={750}>
              <IconCheck
                stroke={2.5}
                onClick={() => confirmReviewedHandlers.open()}
              />
            </Tooltip>
          </ActionIcon>
          <ActionIcon variant="transparent" color="gray">
            <Tooltip label="Update" openDelay={750}>
              <IconPencil
                stroke={1.5}
                onClick={() => displayEditHandlers.open()}
              />
            </Tooltip>
          </ActionIcon>
          <ActionIcon variant="transparent" color="gray">
            <Tooltip label="Delete" openDelay={750}>
              <IconTrash
                stroke={1.5}
                onClick={() => confirmDeleteHandlers.open()}
              />
            </Tooltip>
          </ActionIcon>
        </ActionIcon.Group>
      </Center>
    </>
  )
}

interface ActionConfirmationProps {
  onConfirm: () => void
  confirmHandler: UseDisclosureHandlers
  label: string
  color?: MantineColor
}

const ActionConfirmation = ({
  onConfirm,
  confirmHandler,
  label,
  color,
}: ActionConfirmationProps) => {
  const delayedHideConfirm = useDebouncedCallback(() => {
    confirmHandler.close()
  }, 100)
  const ref = useClickOutside(() => delayedHideConfirm())

  return (
    <div ref={ref}>
      <Center>
        <Button
          variant="filled"
          color={color}
          size="compact-sm"
          onClick={onConfirm}
        >
          {label}
        </Button>
      </Center>
    </div>
  )
}

mount(App)
