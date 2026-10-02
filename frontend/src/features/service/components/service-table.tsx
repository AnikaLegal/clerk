import { Center, Group, Loader, Table, Text } from '@mantine/core'
import { IconExclamationCircle } from '@tabler/icons-react'
import api, { Issue, Service, ServiceCategory } from 'api'
import { RichTextDisplay } from 'comps/rich-text'
import { enqueueSnackbar } from 'notistack'
import React, { useEffect } from 'react'
import { ErrorResult, getAPIErrorMessage } from 'utils'
import { SERVICE_TYPES } from '../schema'
import { ServiceActionIconGroup } from './service-actions'

interface ServiceTableProps {
  issue: Issue
  category: ServiceCategory
  canChange: boolean
}

const COLUMNS: Record<ServiceCategory, string[]> = {
  DISCRETE: ['Type', 'Date', 'Count', 'Notes'],
  ONGOING: ['Type', 'Start date', 'Finish date', 'Notes'],
}

export const ServiceTable = ({
  issue,
  category,
  canChange,
}: ServiceTableProps) => {
  const result = api.useGetCaseServicesQuery({ id: issue.id, category })
  const noun = category.toLowerCase()

  useEffect(() => {
    if (result.isError) {
      enqueueSnackbar(
        getAPIErrorMessage(
          result.error as ErrorResult,
          `Could not load ${noun} services`
        ),
        { variant: 'error' }
      )
    }
  }, [result.isError, result.error, noun])

  const columnCount = COLUMNS[category].length + (canChange ? 1 : 0)

  return (
    <Table
      withColumnBorders
      withTableBorder
      verticalSpacing="xs"
      fz="md"
      mt="lg"
    >
      <Table.Thead>
        <Table.Tr>
          {COLUMNS[category].map((label) => (
            <Table.Th key={label}>{label}</Table.Th>
          ))}
          {canChange && <Table.Th w="1%"></Table.Th>}
        </Table.Tr>
      </Table.Thead>
      <Table.Tbody>
        <ServiceTableBody
          result={result}
          issue={issue}
          category={category}
          canChange={canChange}
          columnCount={columnCount}
        />
      </Table.Tbody>
    </Table>
  )
}

interface ServiceTableBodyProps extends ServiceTableProps {
  result: ReturnType<typeof api.useGetCaseServicesQuery>
  columnCount: number
}

const ServiceTableBody = ({
  result,
  issue,
  category,
  canChange,
  columnCount,
}: ServiceTableBodyProps) => {
  const noun = category.toLowerCase()

  if (result.isError) {
    return (
      <MessageRow columnCount={columnCount}>
        <Group justify="center" gap="xs" c="red">
          <IconExclamationCircle />
          <Text>Could not load {noun} services</Text>
        </Group>
      </MessageRow>
    )
  }
  if (result.isLoading) {
    return (
      <MessageRow columnCount={columnCount}>
        <Loader />
      </MessageRow>
    )
  }

  const services = result.data || []
  if (services.length < 1) {
    return (
      <MessageRow columnCount={columnCount}>
        No {noun} services found
      </MessageRow>
    )
  }

  return (
    <>
      {services.map((service) => (
        <ServiceTableRow
          key={service.id}
          issue={issue}
          service={service}
          canChange={canChange}
        />
      ))}
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

const ServiceTableRow = ({
  issue,
  service,
  canChange,
}: {
  issue: Issue
  service: Service
  canChange: boolean
}) => (
  <Table.Tr>
    <Table.Td>{SERVICE_TYPES[service.category][service.type]}</Table.Td>
    <Table.Td>{service.started_at}</Table.Td>
    <Table.Td>
      {service.category === 'DISCRETE' ? service.count : service.finished_at}
    </Table.Td>
    <Table.Td maw="300px">
      {service.notes && <RichTextDisplay content={service.notes} />}
    </Table.Td>
    {canChange && (
      <Table.Td w="1%">
        <ServiceActionIconGroup issue={issue} service={service} />
      </Table.Td>
    )}
  </Table.Tr>
)
